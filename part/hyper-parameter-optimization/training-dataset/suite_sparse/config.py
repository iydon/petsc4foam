import pathlib as p


ROOT = p.Path(__file__).absolute().parent

CACHE = ROOT / 'cache'
DATA = CACHE / 'data'
META = CACHE / 'meta.json'
SPY = CACHE / 'spy'
ZIP = CACHE / 'zip'
