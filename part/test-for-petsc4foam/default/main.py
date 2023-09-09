import functools as f
import os
import pathlib as p
import shutil
import subprocess as sp
import time
import typing as t

import typing_extensions as te


P = te.ParamSpec('P')
Kwargs = te.ParamSpecKwargs(P)


class Tutorial:

    root = p.Path(os.environ['FOAM_TUTORIALS'])

    def __init__(self, directory: str) -> None:
        self._directory = p.Path(directory)
        self._par = self._directory / 'Allrun'
        self._parp = self._directory / 'Allrun-parallel'
        self._pac = self._directory / 'Allclean'
        self._p0 = self._directory / '0.orig'
        self._psc = self._directory / 'system' / 'controlDict'
        self._psd = self._directory / 'system' / 'decomposeParDict'
        self._psfa = self._directory / 'system' / 'faSolution'
        self._psfv = self._directory / 'system' / 'fvSolution'

    @classmethod
    def iterValids(cls) -> t.Iterator[te.Self]:
        for path in cls.root.rglob('controlDict'):
            self = cls(path.parents[1])
            if self.is_valid():
                yield self

    @property
    def directory(self) -> p.Path:
        return self._directory

    @f.cached_property
    def application(self) -> str:
        return self._fd(f'{self._psc} -entry application -value')

    @f.cached_property
    def number_of_subdomains(self) -> int:
        if self._psd.exists():
            return int(self._fd(f'{self._psd} -entry numberOfSubdomains -value'))
        else:
            return 1

    @property
    def is_parallel(self) -> bool:
        return self._parp.exists() and self.number_of_subdomains > 1

    def is_valid(self) -> bool:
        for func in [
            self._valid_exists, self._valid_allrun,
            self._valid_control_dict, self._valid_cyclic_ami,
        ]:
            try:
                if not func():
                    return False
            except Exception:
                return False
        return True

    def copy(self, dst: str) -> te.Self:
        directory = dst / self._directory.relative_to(self.root)
        shutil.copytree(self._directory, directory, dirs_exist_ok=True)
        return self.__class__(directory)

    def hook_foam(self) -> te.Self:
        self._fd(f'{self._psc} -entry startFrom -set startTime')
        return self

    def hook_petsc(self) -> te.Self:
        # faSolution, fvSolution
        for path in filter(p.Path.exists, [self._psfv, self._psfa]):
            for key in self._fd(f'{path} -entry solvers -keywords').splitlines():
                self._fd(f'{path} -entry solvers/{key}/solver -set petsc')
                self._fd(f'{path} -entry solvers/{key}/petsc -set {{}}')
                self._fd(f'{path} -entry solvers/{key}/preconditioner -remove')
        # controlDict
        self._fd(f'{self._psc} -entry libs -set "(petscFoam)"')
        return self

    def all_run_or_parallel(self, auto: bool = True, timeout: float = 300.0, delete: bool = False) -> bool:
        script = self._parp if auto and self.is_parallel else self._par
        try:
            flag = self._raw(script.as_posix(), timeout=timeout).returncode == 0
        except Exception:
            flag = False
        if delete and not flag:
            self.all_delete()
        return flag

    def all_delete(self) -> None:
        assert not self._directory.is_relative_to(self.root)

        shutil.rmtree(self._directory, ignore_errors=True)
        for path in self._directory.parents:
            if list(path.iterdir()):
                break
            else:
                path.rmdir()

    def run_or_parallel(self, auto: bool = True, timeout: float = 900.0, delete: bool = False) -> bool:
        source = '. $WM_PROJECT_DIR/bin/tools/RunFunctions'
        func = 'runParallel' if auto and self.is_parallel else 'runApplication'
        cmd = f'{source} && {func} {self.application}'
        log = self._directory / f'log.{self.application}'
        log.exists() and log.unlink()
        try:
            flag = self._raw(cmd, timeout=timeout).returncode == 0
        except Exception:
            flag = False
        if delete and not flag:
            self.all_delete()
        return flag

    def run_or_parallel_timer(self, auto: bool = True, timeout: float = 900.0, delete: bool = False) -> t.Optional[float]:
        tic = time.time()
        flag = self.run_or_parallel(auto, timeout, delete)
        toc = time.time()
        return toc - tic if flag else None

    def _raw(self, cmd: str, **kwargs: Kwargs) -> sp.CompletedProcess:
        kwargs = {'shell': True, 'cwd': self._directory, 'capture_output': True, **kwargs}
        return sp.run(cmd, **kwargs)

    def _run(self, cmd: str, **kwargs: Kwargs) -> str:
        return self._raw(cmd, **kwargs).stdout.decode().strip()

    def _fd(self, cmd: str) -> str:
        return self._run(f'foamDictionary {cmd}')

    def _valid_exists(self) -> bool:
        paths = [self._par, self._pac, self._p0, self._psc, self._psfv]
        return all(map(p.Path.exists, paths))

    def _valid_allrun(self) -> bool:
        text = self._par.read_text()
        if any(cmd in text for cmd in ['./', 'cp ', 'rm ', 'snappyHexMesh']):
            return False
        return True

    def _valid_control_dict(self) -> bool:
        return not self._fd(f'{self._psc} -entry libs')

    def _valid_cyclic_ami(self) -> bool:
        for path in self._p0.iterdir():
            for key in self._fd(f'{path} -entry boundaryField -keywords').splitlines():
                if self._fd(f'{path} -entry boundaryField/{key}/type -value') == 'cyclicAMI':
                    return False
        return True


class TSV:

    def __init__(self, path: str, columns: t.List[str]) -> None:
        self._path = p.Path(path)
        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._append(columns)

    def __contains__(self, key: str) -> bool:
        return str(key) in self._path.read_text()

    def append(self, *parts: str) -> None:
        self._append(parts)

    def _append(self, parts: t.Iterable[str]) -> None:
        with open(self._path, 'a+') as f:
            f.write('\t'.join(map(str, parts)) + '\n')


if __name__ == '__main__':
    import tqdm

    timeout_foam, timeout_petsc = 300.0, 1800.0
    cache = p.Path(__file__).parent / 'cache'
    tsv = TSV('petsc4foam.tsv', ['tutorial', 'application', 'is_parallel', 'time_foam', 'time_petsc'])

    for old in tqdm.tqdm(Tutorial.iterValids(), total=150):
        # init
        new = old.copy(cache).hook_foam()
        keys = new.directory.relative_to(cache), new.application, new.is_parallel
        if keys[0] in tsv:
            continue
        if not new.all_run_or_parallel(timeout=timeout_foam, delete=True):
            tsv.append(*keys, 'nan', 'nan')
            continue
        # foam
        time_foam = new.run_or_parallel_timer(timeout=timeout_foam, delete=True)
        if time_foam is None:
            tsv.append(*keys, -timeout_foam, 'nan')
            continue
        # petsc
        time_petsc = new \
            .hook_petsc() \
            .run_or_parallel_timer(timeout=timeout_petsc, delete=True)
        if time_petsc is None:
            tsv.append(*keys, time_foam, -timeout_petsc)
            continue
        # tsv
        tsv.append(*keys, time_foam, time_petsc)
