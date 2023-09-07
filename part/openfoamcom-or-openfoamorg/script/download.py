import json
import pathlib as p
import shlex
import subprocess as sp
import typing as t

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    tqdm = lambda *args, **kwargs: args[0]


root = p.Path(__file__).parents[1]
openfoam = root / 'cache' / 'OpenFOAM'
urls: t.Dict[str, t.List[t.Tuple[str, str]]] \
    = json.loads((root/'static'/'openfoam.json').read_text())
cmds = {
    'com': ['wget "{url}" -O tmp.tgz', 'mkdir -p tmp', 'tar xf tmp.tgz -C tmp'],
    'org': ['wget "{url}" -O tmp.zip', 'unzip tmp.zip -d tmp'],
}


# download from openfoam.com and openfoam.org
for category in ['com', 'org']:
    (openfoam/category).mkdir(parents=True, exist_ok=True)
    for version, url in tqdm(urls[category], desc=category):
        directory = openfoam / category / version
        if not directory.exists():
            for cmd in cmds[category]:
                args = shlex.split(cmd.format(url=url))
                cp = sp.run(args, capture_output=True, cwd=directory.parent)
                assert cp.returncode==0, cp.stderr.decode()
            next((directory.parent/'tmp').iterdir()) \
                .rename(directory.parent/version)
