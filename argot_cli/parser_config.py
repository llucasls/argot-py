from typing import Iterable, cast

from argot_cli.argot_types import ConfigEntry, ConfigEntries
from argot_cli.argot_utils import validate_entries


class ParserConfig:
    """
    Immutable configuration for the argument parser.

    The configuration defines the set of supported options and their
    types.  Entries are provided as a dictionary mapping option names to
    configuration entries.

    The configuration is normalized and validated during construction.
    The resulting object is immutable.
    """
    __slots__ = ['_entries']
    _entries: dict[str, ConfigEntry]

    def __init__(self, entries: ConfigEntries):
        if isinstance(entries, dict):
            self._entries = entries
        else:
            raise TypeError('input value must be a dict')
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

    def get(self, key: str, /) -> ConfigEntry | None:
        return self._entries.get(key)

    def items(self, /) -> Iterable[tuple[str, ConfigEntry]]:
        return self._entries.items()

    def keys(self, /) -> Iterable[str]:
        return self._entries.keys()

    def values(self, /) -> Iterable[ConfigEntry]:
        return self._entries.values()
