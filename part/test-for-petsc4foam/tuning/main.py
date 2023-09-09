import collections as c
import json
import pathlib as p
import shutil
import subprocess as sp
import time


def copytree(src: p.Path, dst: p.Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for path_src in src.rglob('*'):
        path_dst = dst / path_src.relative_to(src)
        if path_src.is_dir():
            path_dst.mkdir(parents=True, exist_ok=True)
        elif path_src.is_file():
            shutil.copy(path_src, path_dst)


tutorial = p.Path('mixerVessel2D')
src, patches, data = tutorial/'original', tutorial/'patch', tutorial/'data.json'
dst = p.Path('cache')
number = 5

if data.exists():
    exit()

times = c.defaultdict(list)
shutil.rmtree(dst, ignore_errors=True)
copytree(src, dst)
application = sp.run(
    'foamDictionary system/controlDict -entry application -value',
    shell=True, cwd=dst, capture_output=True,
).stdout.decode().strip()
# pre-process
sp.run('./Allrun', shell=True, cwd=dst, capture_output=True)
# original
for _ in range(number):
    tic = time.perf_counter()
    cp = sp.run(application, shell=True, cwd=dst, capture_output=True)
    times['original'].append(time.perf_counter() - tic)
# patches
for patch in patches.iterdir():
    copytree(patch, dst)
    for _ in range(number):
        tic = time.perf_counter()
        cp = sp.run(application, shell=True, cwd=dst, capture_output=True)
        times[patch.name].append(time.perf_counter() - tic)
data.write_text(json.dumps(times))
