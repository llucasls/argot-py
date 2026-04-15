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
    cast,
    overload,
)

from argot_cli.argot_utils import validate_entries


class OptionType(StrEnum):
    FLAG = 'flag'
    TEXT = 'text'
    INT = 'int'
    COUNT = 'count'
    LIST = 'list'
    ALIAS = 'alias'


class FlagEntry(TypedDict):
    type: Literal[OptionType.FLAG]


class TextEntry(TypedDict, total=False):
    type: Literal[OptionType.TEXT]
    default: str


class IntEntry(TypedDict, total=False):
    type: Literal[OptionType.INT]
    default: int


class CountEntry(TypedDict):
    type: Literal[OptionType.COUNT]


class ListEntry(TypedDict, total=False):
    type: Literal[OptionType.LIST]
    sep: str


class AliasEntry(TypedDict):
    type: Literal[OptionType.ALIAS]
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
    __slots__ = ('_frozen',)
    _frozen: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._frozen = False

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
    __slots__ = ('_frozen',)
    _frozen: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._frozen = False

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


class ParserConfig:
    __slots__ = ('_entries')
    _entries: dict[str, ConfigEntry]

    def __init__(self, entries: ConfigEntries):
        if isinstance(entries, dict):
            self._entries = entries
        elif isinstance(entries, list):
            entry_map: dict[str, ConfigEntry] = {}
            for entry in entries:
                name = entry['option']
                new_entry = {k: v for k, v in entry.items() if k != 'option'}
                entry_map[name] = cast(ConfigEntry, new_entry)
            self._entries = entry_map
        else:
            raise TypeError('input value must be a dict or list')
        validate_entries(self._entries)

    def __contains__(self, key: str, /) -> bool:
        return key in self._entries

    def __getitem__(self, key: str, /) -> ConfigEntry:
        return self._entries[key]

    def __len__(self, /) -> int:
        return len(self._entries)

    def __repr__(self, /) -> str:
        name = self.__class__.__name__
        return f'{name}({self._entries!r})'

    def items(self, /) -> Iterable[tuple[str, ConfigEntry]]:
        return self._entries.items()

    def keys(self, /) -> Iterable[str]:
        return self._entries.keys()

    def values(self, /) -> Iterable[ConfigEntry]:
        return self._entries.values()


class Options(ResultMapping[str, OptionValue]):
    """parsed option values (short and long options)"""
    __slots__ = ()


class Parameters(ResultMapping[str, str]):
    """name=value variable assignments"""
    __slots__ = ()


class Operands(ResultList[str]):
    """command-line positional arguments"""
    __slots__ = ()


class ParseResult(TypedDict):
    options: Options
    parameters: Parameters
    operands: Operands
