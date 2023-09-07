import json
import pathlib as p
import typing as t

import matplotlib.pyplot as plt
import seaborn as sns


root = p.Path(__file__).parents[1]
differs: t.Dict[str, t.Dict[str, t.Dict[str, t.Dict[str, int]]]] \
    = json.loads((root/'static'/'differs.json').read_text())

func = lambda l, a, d: (a+d) / (2*l+a-d)
for key, differ in differs.items():
    data = {'version': [], 'ratio': []}
    for version, tutorials in differ.items():
        for ratio in [
            func(value['line.old'], value['addition'], value['deletion'])
            for value in tutorials.values()
        ]:
            data['version'].append(version)
            data['ratio'].append(ratio)
    fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=144)
    sns.boxenplot(data=data, x='version', y='ratio', ax=ax)
    ax.grid()
    fig.tight_layout()
    fig.savefig(root/'static'/'figure'/f'{key}.jpg')
