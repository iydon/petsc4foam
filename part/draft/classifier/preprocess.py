import ast
import collections as c
import itertools as it
import json
import math as m
import pathlib as p
import pickle
import typing as t

import numpy as np
import tqdm

from scipy.io import mmread
from scipy.sparse import coo_matrix


MetricsAll = t.Dict[str, t.Dict[t.Tuple[str, ...], float]]
MetricsBest = t.Dict[str, t.Tuple[str, ...]]


def load_metrics_all(path: p.Path, keys: t.Tuple[str, ...], norm: float) -> MetricsAll:
    ans: MetricsAll = {}
    with open(path, 'r') as file:
        file.readline()
        for line in map(str.strip, file):
            if not line:
                continue
            part, *others = line.split('\t')
            options, metrics = map(ast.literal_eval, others)
            if options is None or metrics is None:
                continue
            option = tuple(options[key] for key in keys)
            if metrics['norm'] > norm:
                continue
            ans \
                .setdefault(part, {}) \
                .setdefault(option, metrics['time'])
    return ans


def resize(matrix: coo_matrix, size: int = 64, flat: bool = True) -> np.ndarray:
    ans = np.zeros((size, size), dtype=np.float64)
    delta = m.ceil(matrix.shape[0] / size)
    rows, cols = matrix.row//delta, matrix.col//delta
    counter = c.Counter(zip(rows, cols))
    for ith, jth, value in zip(rows, cols, matrix.data):
        ans[ith, jth] += value / counter[(ith, jth)]
    ans /= max(1.0, abs(ans.max()), abs(ans.min()))  # normalize
    if flat:
        return ans.flatten()
    else:
        arrays = [
            ans.diagonal(0), *it.chain(*(
                (ans.diagonal(ith), ans.diagonal(-ith))
                for ith in range(1, 32)
            ))
        ]
        return np.concatenate(arrays, axis=0)


root = p.Path(__file__).parent

dir_cache = root / 'cache'
dir_mtx = root.parents[1] / 'hyper-parameter-optimization' / 'training-dataset' / 'foam2mtx' / 'cache' / 'mtx' / '10'
path_metrics = root.parents[1] / 'hyper-parameter-optimization' / 'training-dataset' / 'data_labeling' / 'metrics.tsv'
path_metrics_all = dir_cache / 'metrics_all.pkl'
path_metrics_best = dir_cache / 'metrics_best.pkl'
path_mapper = dir_cache / 'mapper.json'
path_xs = dir_cache / 'xs.npy'
path_ys = dir_cache / 'ys.npy'
option_keys, norm = ('ksp_type', 'pc_type'), 1e-7
length = 32

# metrics_all
if path_metrics_all.exists():
    metrics_all = pickle.loads(path_metrics_all.read_bytes())
else:
    path_metrics_all.parent.mkdir(parents=True, exist_ok=True)
    metrics_all = load_metrics_all(path_metrics, option_keys, norm)
    path_metrics_all.write_bytes(pickle.dumps(metrics_all))
# metrics_best
if path_metrics_best.exists():
    metrics_best = pickle.loads(path_metrics_best.read_bytes())
else:
    path_metrics_best.parent.mkdir(parents=True, exist_ok=True)
    metrics_best = {
        key: min(value, key=value.__getitem__)
        for key, value in metrics_all.items()
    }
    path_metrics_best.write_bytes(pickle.dumps(metrics_best))
# matrices, indices
if path_mapper.exists() and path_xs.exists() and path_ys.exists():
    exit()
matrices, indices = [], []
mappers = tuple(map(lambda x: sorted(set(x)), zip(*metrics_best.values())))
for filename, options in tqdm.tqdm(metrics_best.items()):
    try:
        matrix = resize(mmread(dir_mtx/filename), length)
        index = list(map(lambda mo: list.index(*mo), zip(mappers, options)))
    except Exception:
        continue
    matrices.append(matrix)
    indices.append(index)
path_mapper.write_text(json.dumps(mappers, indent=4))
np.save(path_xs, np.array(matrices))
np.save(path_ys, np.array(indices))
