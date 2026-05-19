from abc import ABCMeta
from enum import StrEnum
from typing import (
    Any,
    Callable,
    Iterable,
    Literal,
    NotRequired,
    SupportsIndex,
    TypedDict,
    Union,
    overload,
)


type OptionType = Union[
    Literal['flag'],
    Literal['text'],
    Literal['int'],
    Literal['float'],
    Literal['count'],
    Literal['list'],
    Literal['alias'],
]


type AliasType = Union[
    Literal['flag'],
    Literal['text'],
    Literal['int'],
    Literal['float'],
    Literal['count'],
    Literal['list'],
]


class FlagEntry(TypedDict):
    """
    Flag option.

    An option without arguments. When present in the command-line, it is
    parsed as True. If the option is not provided, it does not appear in
    the parsed options mapping.
    """
    type: Literal['flag']


class TextEntry(TypedDict, total=False):
    """
    Text option.

    Accepts a string value.

    If a default value is provided, the option may be specified without
    an explicit value. Short options with a default value only accept an
    associated value when provided in the same argument (e.g. "-fvalue").
    """
    type: Literal['text']
    default: str


class IntEntry(TypedDict, total=False):
    """
    Int option.

    Accepts an integer value.

    If a default value is provided, the option may be specified without
    an explicit value. Short options with a default value only accept an
    associated value when provided in the same argument (e.g. "-n58").
    """
    type: Literal['int']
    default: int


class FloatEntry(TypedDict, total=False):
    """
    Float option.

    Accepts a numeric value.

    If a default value is provided, the option may be specified without
    an explicit value. Short options with a default value only accept an
    associated value when provided in the same argument (e.g. "-f0.95").
    """
    type: Literal['float']
    default: float


class CountEntry(TypedDict):
    """
    Count option.

    Each occurrence increments an integer counter. The initial value
    is 0.  If the option is not provided, it does not appear in the
    parsed options mapping.
    """
    type: Literal['count']


class ListEntry(TypedDict, total=False):
    """
    List option.

    Creates a list of strings. Each occurrence is split using the
    configured separator ("," by default), and the resulting values are
    appended to the list.
    """
    type: Literal['list']
    sep: str


class AliasEntry(TypedDict):
    """
    Alias option.

    Refers to another option by name. When parsed, the value is stored
    under the target option's name instead of the alias name.
    """
    type: Literal['alias']
    target: str


type ConfigEntry = Union[
    FlagEntry,
    TextEntry,
    IntEntry,
    FloatEntry,
    CountEntry,
    ListEntry,
    AliasEntry,
]


type ConfigEntries = dict[str, ConfigEntry]


class ParserOptions(TypedDict, total=False):
    """
    ParserConfig configuration flags that don't refer to a single
    command-line option.
    """

    allowUnknown: bool
    parseParameters: bool
    aggregateErrors: bool


class StrictParserOptions(TypedDict, total=True):
    allowUnknown: bool
    parseParameters: bool
    aggregateErrors: bool


class ParserConfigInput(TypedDict):
    """
    The input object for the ParserConfig constructor.
    Contains configuration for specific command-line options
    and general configuration options.
    """

    options: ConfigEntries
    parser: NotRequired[ParserOptions]


type OptionValue = bool | str | int | float | list[str]


class ResultMapping[K, V](dict[K, V], metaclass=ABCMeta):
    """
    Result mapping.
    A dict-like structure used to store parsed key-value pairs.
    Instances can be frozen to prevent further modifications.
    """
    __slots__ = ['_frozen']
    _frozen: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._frozen = False

    def __setattr__(self, name: str, value: Any, /):
        if name == '_frozen':
            object.__setattr__(self, '_frozen', value)
        else:
            raise TypeError(f'Cannot add property {name}')

    def __setitem__(self, key: K, value: V, /):
        if self._frozen:
            raise TypeError('you cannot modify parsed values')
        super().__setitem__(key, value)

    def __delitem__(self, key: K, /):
        if self._frozen:
            raise TypeError('you cannot delete parsed values')
        super().__delitem__(key)

    def clear(self, /):
        if self._frozen:
            raise TypeError('you cannot delete parsed values')
        super().clear()

    def copy(self, /) -> ResultMapping[K, V]:
        cls = self.__class__
        return cls(self.items())

    def pop(self, key: K, /, *args) -> V:
        if self._frozen:
            raise TypeError('you cannot delete parsed values')
        return super().pop(key, *args)

    def popitem(self, /) -> tuple[K, V]:
        if self._frozen:
            raise TypeError('you cannot delete parsed values')
        return super().popitem()

    def setdefault(self, key: K, default=None, /) -> V:
        if self._frozen:
            raise TypeError('you cannot modify parsed values')
        return super().setdefault(key, default)

    def update(self, *args, **kwargs):
        if self._frozen:
            raise TypeError('you cannot modify parsed values')
        super().update(*args, **kwargs)

    def _freeze(self):
        self._frozen = True


class ResultList[T](list[T], metaclass=ABCMeta):
    """
    Result list.
    A list-like structure used to store ordered values.
    Instances can be frozen to prevent further modifications.
    """
    __slots__ = ['_frozen']
    _frozen: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._frozen = False

    def __setattr__(self, name: str, value: Any, /):
        if name == '_frozen':
            object.__setattr__(self, '_frozen', value)
        else:
            raise TypeError(f'Cannot add property {name}')

    @overload
    def __setitem__(self, index: SupportsIndex, value: T, /): ...

    @overload
    def __setitem__(self, index: slice, value: Iterable[T], /): ...

    def __setitem__(self, index, value, /):
        if self._frozen:
            raise TypeError('you cannot modify parsed values')
        super().__setitem__(index, value)

    def __delitem__(self, index: SupportsIndex | slice[Any, Any, Any], /):
        if self._frozen:
            raise TypeError('you cannot delete parsed values')
        super().__delitem__(index)

    def append(self, value: T, /):
        if self._frozen:
            raise TypeError('you cannot add new values')
        super().append(value)

    def clear(self, /):
        if self._frozen:
            raise TypeError('you cannot delete parsed values')
        super().clear()

    def copy(self, /) -> ResultList[T]:
        cls = self.__class__
        return cls(self.__iter__())

    def extend(self, iterable: Iterable[T], /):
        if self._frozen:
            raise TypeError('you cannot add new values')
        super().extend(iterable)

    def insert(self, index: SupportsIndex, value: T, /):
        if self._frozen:
            raise TypeError('you cannot add new values')
        super().insert(index, value)

    def pop(self, index: SupportsIndex = -1, /) -> T:
        if self._frozen:
            raise TypeError('you cannot delete parsed values')
        return super().pop(index)

    def remove(self, value: T, /):
        if self._frozen:
            raise TypeError('you cannot delete parsed values')
        super().remove(value)

    def reverse(self, /):
        if self._frozen:
            raise TypeError('you cannot modify parsed values')
        super().reverse()

    def sort(self, /, *, key: Callable | None = None, reverse=False):
        if self._frozen:
            raise TypeError('you cannot modify parsed values')
        super().sort(key=key, reverse=reverse)

    def _freeze(self):
        self._frozen = True


class Options(ResultMapping[str, OptionValue]):
    """
    Mapping of parsed option values.

    Values are determined by the configuration. Repeated options either
    overwrite previous values or accumulate them, depending on their
    type.

    The mapping is immutable after parsing.
    """
    __slots__ = []


class Parameters(ResultMapping[str, str]):
    """
    Mapping of key/value assignments.

    Parameters are parsed from arguments of the form "key=value" and do
    not depend on the parser configuration.
    """
    __slots__ = []


class Operands(ResultList[str]):
    """
    Positional arguments.

    Operands are arguments that are not parsed as options or parameters.
    The list is immutable after parsing.
    """
    __slots__ = []


class ParseResult(TypedDict):
    options: Options
    parameters: Parameters
    operands: Operands
