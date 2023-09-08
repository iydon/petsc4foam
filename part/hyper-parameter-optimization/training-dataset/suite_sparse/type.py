import pathlib as p
import typing as t

import typing_extensions as te


# type variables (private, public)
T1, T2, T3 = t.TypeVar('T1'), t.TypeVar('T2'), t.TypeVar('T3')
Ta, Tb, Tc = t.TypeVar('Ta'), t.TypeVar('Tb'), t.TypeVar('Tc')
P = te.ParamSpec('P')

# generics
DictInt = t.Dict[int, T1]
DictStr = t.Dict[str, T1]

Func0 = t.Callable[[], T1]
Func1 = t.Callable[[T1], T2]
Func2 = t.Callable[[T1, T2], T3]

Pair = t.Tuple[T1, T2]
Triple = t.Tuple[T1, T2, T3]
TupleSeq = t.Tuple[T1, ...]

# types with abstract names
Kwargs = te.ParamSpecKwargs(P)
Strings = t.List[str]

# types with specific names (if several files use this type, put it here)
Command = t.Union[str, Strings]
Path = t.Union[str, p.Path]
