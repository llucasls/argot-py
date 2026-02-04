from enum import StrEnum
from typing import Literal, TypedDict, Union


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

type OptionValue = bool | str | int | list[str]
