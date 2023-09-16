import json
import math as m
import pathlib as p

import matplotlib.pyplot as plt
import numpy as np
import tqdm


root = p.Path(__file__).parent
dir_cache = root / 'cache'
dir_image = dir_cache / 'image'
xs: np.ndarray = np.load(dir_cache/'xs.npy')
ys: np.ndarray = np.load(dir_cache/'ys.npy')
mappers = json.loads((dir_cache/'mapper.json').read_text())

iterations = enumerate(zip(xs, ys))
for ith, (x, y) in tqdm.tqdm(iterations, total=len(xs)):
    key = '+'.join(
        str(mapper[yi])
        for mapper, yi in zip(mappers, y)
    )
    path = dir_image / key / f'{ith}.png'
    path.parent.mkdir(parents=True, exist_ok=True)
    size = int(m.sqrt(x.size))
    x.resize((size, size))
    # plot
    fig, ax = plt.subplots(1, 1, dpi=400)
    ax.spy(x)
    fig.tight_layout()
    fig.savefig(path)
    plt.close('all')
