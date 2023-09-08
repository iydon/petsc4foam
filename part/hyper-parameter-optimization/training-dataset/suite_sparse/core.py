import io
import json
import pathlib as p
import tarfile
import typing as t

import matplotlib.pyplot as plt
import numpy as np
import requests
import tqdm
import typing_extensions as te

from math import ceil
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from .config import DATA, META, SPY, ZIP
from .type import DictStr, Func0, Kwargs, Strings
from .util import mkdir


class SuiteSparseMatrixCollection:
    def __init__(self, https: bool = True) -> None:
        self._scheme = 'https://' if https else 'http://'
        self._links = json.loads(META.read_text()) if META.exists() else self._meta()

    @classmethod
    def fromHttp(cls) -> te.Self:
        return cls(https=False)

    def update_data(self, overwrite: bool = False, filter_kwargs: DictStr = {}) -> te.Self:
        for link in tqdm.tqdm(self._links):
            parts = urlsplit(link)
            path = p.Path(parts.path).relative_to('/MM/')
            self._try(
                lambda: self._data_download(parts.netloc+parts.path, path, overwrite),
                lambda: self._data_filter(path, **filter_kwargs),
                lambda: self._data_extract(path, overwrite),
            )
        return self

    def update_meta(self) -> te.Self:
        self._links = self._meta()
        return self

    def spy(self, shape: t.Optional[int] = None, overwrite: bool = False) -> te.Self:
        mkdir(SPY)
        for path in tqdm.tqdm(list(DATA.rglob('*.mtx'))):
            self._spy(path, shape, overwrite)
        return self

    def _get(self, url_without_scheme: str, **kwargs: Kwargs) -> requests.Response:
        proxy = 'http://localhost:20171'
        kwargs['proxies'] = {'http': proxy, 'https': proxy}
        return requests.get(self._scheme+url_without_scheme, **kwargs)

    def _get_soup(self, url_without_scheme: str, **kwargs: Kwargs) -> BeautifulSoup:
        response = self._get(url_without_scheme, **kwargs)
        return BeautifulSoup(response.content, 'html.parser')

    def _data_download(self, url: str, src: p.Path, overwrite: bool) -> None:
        dst = ZIP / src
        if not overwrite and dst.exists():
            return
        mkdir(dst, parent=True).write_bytes(self._get(url).content)

    def _data_extract(self, src: p.Path, overwrite: bool) -> None:
        dst = mkdir(DATA / src.parent) / src.name.rsplit('.', maxsplit=2)[0]
        if not overwrite and dst.exists():
            return
        with tarfile.TarFile.open(ZIP/src, 'r:gz') as tar:
            for info in tar:
                if not info.isreg():
                    continue
                with tar.extractfile(info) as file:
                    if self._check_mtx(file):
                        tar.extract(info, dst.parent)

    def _data_filter(self, src: p.Path, byte_min: int, byte_max: int) -> None:
        size = (ZIP/src).stat().st_size
        if byte_max <= size or size <= byte_min:
            raise NotImplementedError

    def _meta(self) -> Strings:
        soup = self._get_soup('sparse.tamu.edu', params={'per_page': 'All'})
        links = [
            item.find_all('a')[-1].attrs['href']
            for item in soup.find(id='matrices').find_all(class_='column-download')
        ]
        mkdir(META, parent=True).write_text(json.dumps(links))
        return links

    def _spy(self, src: p.Path, shape: t.Optional[int] = None, overwrite: bool = False) -> None:
        dst = SPY / '+'.join(src.relative_to(DATA).with_suffix('.png').parts)
        if not overwrite and dst.exists():
            return
        with open(src, 'r') as file:
            symmetric = file.readline().split()[4] in {'symmetric', 'skew-symmetric', 'hermitian'}
            while True:
                line = file.readline()
                if not line.startswith('%'):
                    break
            size, _, nz = map(int, line.split())  # row == col
            shape, delta = (size, 1.0) if shape is None else (shape, size/shape)
            image = np.zeros((shape, shape), dtype=np.bool_)
            for _ in range(nz):
                ith, jth = map(int, file.readline().split()[:2])
                image[ceil(ith/delta)-1, ceil(jth/delta)-1] = True
        if symmetric:
            image |= image.T
        self._imsave(dst, image)

    def _check_mtx(self, file: io.BufferedReader) -> bool:
        if file.readline().split()[:3] != [b'%%MatrixMarket', b'matrix', b'coordinate']:
            return False
        while True:
            line = file.readline()
            if not line.startswith('%'):
                break
        row, col = map(int, line.split()[:2])
        return row == col

    def _imsave(self, path: p.Path, matrix: np.ndarray) -> None:
        plt.imsave(path, matrix, cmap='gray')

    def _try(self, *funcs: Func0[None]) -> None:
        for func in funcs:
            try:
                func()
            except Exception:
                return
