import collections as c
import difflib
import functools as f
import json
import pathlib as p
import typing as t


T = t.TypeVar('T')
DictStr2 = t.Dict[str, t.Dict[str, T]]
DictStr4 = DictStr2[DictStr2[T]]
Path = t.Union[str, p.Path]


class Differ:
    def __init__(self, old: Path, new: Path) -> None:
        self._old = p.Path(old)
        self._new = p.Path(new)

    def info(self) -> t.Dict[str, int]:
        files_old = self._files(self._old)
        files_new = self._files(self._new)
        addition, deletion = 0, 0
        for key in files_old.keys() - files_new.keys():
            deletion += len(files_old[key])
        for key in files_new.keys() - files_old.keys():
            addition += len(files_new[key])
        for key in files_old.keys() & files_new.keys():
            for line in difflib.unified_diff(files_old[key], files_new[key]):
                if line.startswith('+++') or line.startswith('---'):
                    pass
                elif line.startswith('+'):
                    addition += 1
                elif line.startswith('-'):
                    deletion += 1
        return {
            'line.old': sum(map(len, files_old.values())),
            'addition': addition,
            'deletion': deletion,
        }

    def _files(self, directory: p.Path) -> t.Dict[str, t.List[str]]:
        ans = {}
        for path in directory.rglob('*'):
            if path.is_file():
                try:
                    text = path.read_text()
                except UnicodeDecodeError:
                    pass
                else:
                    key = path.relative_to(directory).as_posix()
                    ans[key] = text.splitlines(keepends=True)
        return ans


class OpenFOAM:
    def __init__(self, path: Path) -> None:
        self._path = p.Path(path)

    def relative(self, path: p.Path) -> str:
        return path.relative_to(self._path).as_posix()

    def tutorials(self) -> t.Iterator[p.Path]:
        yield from self._tutorials(self._path/'tutorials')

    def _tutorials(self, path: p.Path) -> t.Iterator[p.Path]:
        if path.is_dir():
            parts = ['0', '0.orig', '0.org', 'constant', 'system']
            if any((path/part).exists() for part in parts):
                yield path
            else:
                for subpath in path.iterdir():
                    yield from self._tutorials(subpath)


class Main:
    _root = p.Path(__file__).parents[1]
    _openfoam = _root / 'cache' / 'OpenFOAM'
    _categories = ['com', 'org']
    _urls: t.Dict[str, t.List[t.Tuple[str, str]]] \
        = json.loads((_root/'static'/'openfoam.json').read_text())

    @f.lru_cache(maxsize=None)
    def tutorials(self) -> DictStr2[t.List[str]]:
        # {category -> version -> [...] as cases}
        ans = self._tree()
        for category in self._categories:
            for version, _ in self._urls[category]:
                of = OpenFOAM(self._openfoam/category/version)
                ans[category][version] = [
                    of.relative(tutorial)
                    for tutorial in of.tutorials()
                ]
        return ans

    def differs(self) -> DictStr4[int]:
        # {category -> version (new) -> case -> {...} as info}
        ans = self._tree()
        tutorials = self.tutorials()
        for category in self._categories:
            versions = [version for version, _ in self._urls[category]]
            for version_old, version_new in zip(versions, versions[1:]):
                keys_old = tutorials[category][version_old]
                keys_new = tutorials[category][version_new]
                for key in set(keys_old) & set(keys_new):
                    path_old = self._openfoam / category / version_old / key
                    path_new = self._openfoam / category / version_new / key
                    ans[category][version_new][key] = Differ(path_old, path_new).info()
        return ans

    def doit(self, filename: str, overwrite: bool = False) -> None:
        path = self._root / 'static' / filename
        if overwrite or not path.exists():
            differs = self.differs()
            path.write_text(json.dumps(differs))

    def _tree(self) -> c.defaultdict:
        return c.defaultdict(self._tree)


if __name__ == '__main__':
    Main().doit('differs.json', overwrite=False)
