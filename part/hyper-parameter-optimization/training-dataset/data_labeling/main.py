import ast
import itertools as it
import pathlib as p
import subprocess as sp
import typing as t

import tqdm


Number = t.Union[int, float]
Metrics = t.Dict[str, Number]


def txt2bin(src: p.Path, dst: p.Path) -> bool:
    cp = sp.run([
        'txt2bin', '--type', 'mtx', '--base', '1',
        '--in', src.as_posix(), '--out', dst.as_posix(),
    ], capture_output=True)
    return cp.returncode == 0


def test4solve(path: p.Path, timeout: float, number: int = 1000, **options: str) -> t.Optional[Metrics]:
    extras = [[f'-{key}', str(val)] for key, val in options.items()]
    try:
        cp = sp.run([
            'test4solve', '--A', path.as_posix(), '--number', str(number),
            *it.chain(*extras),
        ], capture_output=True, timeout=timeout)
        if cp.returncode != 0:
            return None
        func = lambda key, val: (key, ast.literal_eval(val))  # inf
        return dict(
            func(*line.split('\t'))
            for line in cp.stdout.decode().splitlines()
        )
    except Exception:
        return None


class TSV:

    def __init__(self, path: str, columns: t.List[str]) -> None:
        self._path = p.Path(path)
        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._append(columns)

    def __contains__(self, key: str) -> bool:
        with open(self._path, 'r') as f:
            for line in f:
                if key in line.strip().split('\t'):
                    return True
        return False

    def append(self, *parts: str) -> None:
        self._append(parts)

    def _append(self, parts: t.Iterable[str]) -> None:
        with open(self._path, 'a+') as f:
            f.write('\t'.join(map(str, parts)) + '\n')


root = p.Path(__file__).parent
dir_src = root.parents[1] / 'training-dataset' / 'foam2mtx' / 'cache' / 'mtx' / '10'
dir_dst = root / 'cache'
tsv = TSV(root/'metrics.tsv', ['path', 'options', 'metrics'])
default = {'timeout': 100*0.1, 'number': 100, 'ksp_rtol': 1e-7}
ksp_types = {'richardson', 'chebyshev', 'cg', 'gmres', 'bicg'}
pc_types = {'none', 'jacobi', 'lu', 'asm', 'ilu', 'gamg'}

dir_dst.mkdir(parents=True, exist_ok=True)
paths = list(dir_src.rglob('0'))
for path_src in tqdm.tqdm(paths):
    if not path_src.is_file():
        continue
    key = path_src.relative_to(dir_src).as_posix()
    path_dst = dir_dst / key
    if key in tsv:
        continue
    # txt2bin
    if not path_dst.exists():
        path_dst.parent.mkdir(parents=True, exist_ok=True)
        if not txt2bin(path_src, path_dst):
            tsv.append(key, 'None', 'None')
            tsv.append()
            continue
    # test4solve
    for ksp_type, pc_type in it.product(ksp_types, pc_types):
        options = {'ksp_type': ksp_type, 'pc_type': pc_type}
        metrics = test4solve(path_dst, **default, **options)
        tsv.append(key, repr(options), repr(metrics))
    tsv.append()
