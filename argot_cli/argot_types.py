from abc import ABCMeta
from enum import StrEnum
from typing import (
    Any,
    Callable,
    Iterable,
    Literal,
    SupportsIndex,
    TypedDict,
    Union,
    overload,
)


type OptionType = Union[
    Literal['flag'],
    Literal['text'],
    Literal['int'],
    Literal['count'],
    Literal['list'],
    Literal['alias'],
]


type AliasType = Union[
    Literal['flag'],
    Literal['text'],
    Literal['int'],
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
    CountEntry,
    ListEntry,
    AliasEntry,
]


class LabeledEntryBase(TypedDict):
    option: str


class LabeledFlagEntry(LabeledEntryBase, FlagEntry): ...
class LabeledTextEntry(LabeledEntryBase, TextEntry): ...
class LabeledIntEntry(LabeledEntryBase, IntEntry): ...
class LabeledCountEntry(LabeledEntryBase, CountEntry): ...
class LabeledListEntry(LabeledEntryBase, ListEntry): ...
class LabeledAliasEntry(LabeledEntryBase, AliasEntry): ...


type LabeledEntry = Union[
    LabeledFlagEntry,
    LabeledTextEntry,
    LabeledIntEntry,
    LabeledCountEntry,
    LabeledListEntry,
    LabeledAliasEntry,
]


type ConfigEntries = dict[str, ConfigEntry] | list[LabeledEntry]


type OptionValue = bool | str | int | list[str]


class ResultMapping[K, V](dict[K, V], metaclass=ABCMeta):
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
            raise TypeError('you cannot modify option values')
        super().__setitem__(key, value)

    def __delitem__(self, key: K, /):
        if self._frozen:
            raise TypeError('you cannot delete parsed options')
        super().__delitem__(key)

    def clear(self, /):
        if self._frozen:
            raise TypeError('you cannot delete parsed options')
        super().clear()

    def copy(self, /) -> ResultMapping[K, V]:
        cls = self.__class__
        return cls(self.items())

    def pop(self, key: K, /, *args) -> V:
        if self._frozen:
            raise TypeError('you cannot delete parsed options')
        return super().pop(key, *args)

    def popitem(self, /) -> tuple[K, V]:
        if self._frozen:
            raise TypeError('you cannot delete parsed options')
        return super().popitem()

    def setdefault(self, key: K, default=None, /) -> V:
        if self._frozen:
            raise TypeError('you cannot modify option values')
        return super().setdefault(key, default)

    def update(self, *args, **kwargs):
        if self._frozen:
            raise TypeError('you cannot modify option values')
        super().update(*args, **kwargs)

    def _freeze(self):
        self._frozen = True


class ResultList[T](list[T], metaclass=ABCMeta):
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
            raise TypeError('you cannot modify parsed operands')
        super().__setitem__(index, value)

    def __delitem__(self, index: SupportsIndex | slice[Any, Any, Any], /):
        if self._frozen:
            raise TypeError('you cannot delete parsed operands')
        super().__delitem__(index)

    def append(self, value: T, /):
        if self._frozen:
            raise TypeError('you cannot add new operands')
        super().append(value)

    def clear(self, /):
        if self._frozen:
            raise TypeError('you cannot delete parsed operands')
        super().clear()

    def copy(self, /) -> ResultList[T]:
        cls = self.__class__
        return cls(self.__iter__())

    def extend(self, iterable: Iterable[T], /):
        if self._frozen:
            raise TypeError('you cannot add new operands')
        super().extend(iterable)

    def insert(self, index: SupportsIndex, value: T, /):
        if self._frozen:
            raise TypeError('you cannot add new operands')
        super().insert(index, value)

    def pop(self, index: SupportsIndex = -1, /) -> T:
        if self._frozen:
            raise TypeError('you cannot delete parsed operands')
        return super().pop(index)

    def remove(self, value: T, /):
        if self._frozen:
            raise TypeError('you cannot delete parsed operands')
        super().remove(value)

    def reverse(self, /):
        if self._frozen:
            raise TypeError('you cannot modify parsed operands')
        super().reverse()

    def sort(self, /, *, key: Callable | None = None, reverse=False):
        if self._frozen:
            raise TypeError('you cannot modify parsed operands')
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
    __slots__ = ()


class Parameters(ResultMapping[str, str]):
    """
    Mapping of key/value assignments.

    Parameters are parsed from arguments of the form "key=value" and do
    not depend on the parser configuration.
    """
    __slots__ = ()


class Operands(ResultList[str]):
    """
    Positional arguments.

    Operands are arguments that are not parsed as options or parameters.
    The list is immutable after parsing.
    """
    __slots__ = ()


class ParseResult(TypedDict):
    options: Options
    parameters: Parameters
    operands: Operands
