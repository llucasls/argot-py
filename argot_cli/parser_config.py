from typing import Iterable, cast

from argot_cli.argot_types import ConfigEntry, ConfigEntries
from argot_cli.argot_utils import validate_entries


class ParserConfig:
    """
    Immutable configuration for the argument parser.

    The configuration defines the set of supported options and their types.

    Input may be provided as:
    - a mapping of option names to configuration entries
    - a list of labeled entries

    The configuration is normalized and validated during construction.
    The resulting object is immutable.
    """
    __slots__ = ['_entries']
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

    def get(self, key: str, /) -> ConfigEntry | None:
        return self._entries.get(key)

    def items(self, /) -> Iterable[tuple[str, ConfigEntry]]:
        return self._entries.items()

    def keys(self, /) -> Iterable[str]:
        return self._entries.keys()

    def values(self, /) -> Iterable[ConfigEntry]:
        return self._entries.values()
