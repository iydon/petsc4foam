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

def test4solve(path: p.Path, number: int = 1000, **kwargs: str) -> t.Optional[Metrics]:
    extras = [[f'-{key}', str(val)] for key, val in kwargs.items()]
    cp = sp.run([
        'test4solve', '--A', path.as_posix(), '--number', str(number),
        *it.chain(*extras),
    ], capture_output=True)
    if cp.returncode == 0:
        func = lambda key, val: (key, ast.literal_eval(val))
        return dict(
            func(*line.split('\t'))
            for line in cp.stdout.decode().splitlines()
        )

def append_line(path: p.Path, line: str = '') -> None:
    with open(path, 'a+') as file:
        file.write(line + '\n')


root = p.Path(__file__).parent
dir_src = root.parent / 'training-dataset' / 'foam2mtx' / 'cache' / 'mtx' / '10'
dir_dst = root / 'cache'
path_log = root / 'metrics.tsv'
default = {'number': 100, 'ksp_rtol': 1e-7}
ksp_types = {'richardson', 'chebyshev', 'cg', 'gmres', 'bicg'}
pc_types = {'none', 'jacobi', 'lu', 'asm', 'ilu', 'gamg'}

dir_dst.mkdir(parents=True, exist_ok=True)
paths = list(dir_src.rglob('0'))
for path_src in tqdm.tqdm(paths):
    if not path_src.is_file():
        continue
    path_rel = path_src.relative_to(dir_src).as_posix()
    path_dst = dir_dst / path_rel
    # txt2bin
    if not path_dst.exists():
        path_dst.parent.mkdir(parents=True, exist_ok=True)
        if not txt2bin(path_src, path_dst):
            continue
    # test4solve
    for ksp_type, pc_type in it.product(ksp_types, pc_types):
        kwargs = {'ksp_type': ksp_type, 'pc_type': pc_type}
        metrics = test4solve(path_dst, **default, **kwargs)
        append_line(path_log, f'{path_rel}\t{kwargs!r}\t{metrics!r}')
    append_line(path_log)
