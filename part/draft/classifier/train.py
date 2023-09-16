import collections as c
import pathlib as p
import typing as t

import joblib
import numpy as np

from sklearn.metrics import accuracy_score, f1_score, make_scorer, precision_score, recall_score
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier as Classifier


def balance(xs: np.ndarray, ys: np.ndarray) -> t.Tuple[np.ndarray, np.ndarray]:
    data = c.defaultdict(list)
    for x, y in zip(xs, ys):
        data[y].append(x)
    maximal = max(len(xs) for xs in data.values())
    for y, xs in data.items():
        count = len(xs)
        for ith in np.random.choice(range(count), maximal-count):
            x = data[y][ith]
            data[y].append(x + 0.1 * np.random.random(x.size) * (x!=0.0))
    ans_xs, ans_ys = [], []
    for y, xs in data.items():
        for x in xs:
            ans_xs.append(x)
            ans_ys.append(y)
    idx = np.random.permutation(range(len(ans_xs)))
    return np.array(ans_xs)[idx], np.array(ans_ys)[idx]


root = p.Path(__file__).parent
xs: np.ndarray = np.load(root/'cache'/'xs.npy')
ys: np.ndarray = np.load(root/'cache'/'ys.npy')
path_model = root / 'cache' / 'model.pkl'

# data-balance
keys = sorted(set(map(tuple, ys)))
ys = np.array(list(map(keys.index, map(tuple, ys))))
xs, ys = balance(xs, ys)

# cross-validation
for scoring in [
    make_scorer(accuracy_score),
    make_scorer(precision_score, average='macro'),
    make_scorer(recall_score, average='macro'),
    make_scorer(f1_score, average='macro'),
]:
    clf = Classifier()
    scores = cross_val_score(clf, xs, ys, scoring=scoring, cv=5, n_jobs=-1)
    print(scoring, scores.mean())

# save-model
clf = Classifier().fit(xs, ys)
joblib.dump(clf, path_model)
