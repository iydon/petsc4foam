import pathlib as p
import subprocess as sp

from .type import Command, Kwargs, Path


class run:
    '''Run command'''

    @classmethod
    def origin(cls, command: Command, **kwargs: Kwargs) -> sp.CompletedProcess:
        return sp.run(command, **kwargs)

    @classmethod
    def origin_check(cls, command: Command, **kwargs: Kwargs) -> sp.CompletedProcess:
        return cls._check(cls.origin(command, **kwargs))

    @classmethod
    def _check(cls, cp: sp.CompletedProcess) -> sp.CompletedProcess:
        assert cp.returncode == 0, cp.stderr

        return cp

    o = origin
    oc = origin_check


def mkdir(path: Path, parent: bool = False) -> p.Path:
    directory = p.Path(path)
    (directory.parent if parent else directory) \
        .mkdir(parents=True, exist_ok=True)
    return directory
