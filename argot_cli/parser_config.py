from typing import Iterable, cast

from argot_cli.argot_types import (
    ConfigEntry,
    ConfigEntries,
    ParserConfigInput,
    StrictParserOptions,
)
from argot_cli.argot_utils import validate_entries, validate_entries_aggregate


class ParserConfig:
    """
    Immutable configuration for the argument parser.

    The configuration defines the set of supported options and their
    types. Entries are provided as a dictionary mapping option names to
    configuration entries.

    The configuration is normalized and validated during construction.
    The resulting object is immutable.
    """
    __slots__ = ['_entries', '_parser', '_size']
    _entries: dict[str, ConfigEntry]
    _parser: StrictParserOptions
    _size: int

    def __init__(self, configs: ParserConfigInput, /):
        if not isinstance(configs, dict):
            raise TypeError('input value must be a dict')

        options = configs.get('options')
        parser = configs.get('parser')
        if not isinstance(options, dict):
            raise TypeError('"options" value must be a dict')
        elif parser is not None and not isinstance(parser, dict):
            raise TypeError('"parser" value must be a dict')

        if parser is None:
            self._parser = {
                'allowUnknown': False,
                'parseParameters': True,
                'aggregateErrors': True,
            }
        else:
            self._parser = {
                'allowUnknown': parser.get('allowUnknown', False),
                'parseParameters': parser.get('parseParameters', True),
                'aggregateErrors': parser.get('aggregateErrors', True),
            }

        self._size = 0
        entry_map: ConfigEntries = {}
        for key, value in options.items():
            entry_map[key] = value.copy()
            self._size += 1
        self._entries = entry_map

        if self._parser['aggregateErrors']:
            validate_entries_aggregate(self._entries)
        else:
            validate_entries(self._entries)

    def __contains__(self, key: str, /) -> bool:
        return key in self._entries

    def __getitem__(self, key: str, /) -> ConfigEntry:
        return self._entries[key]

    def __len__(self, /) -> int:
        return self._size

    def __repr__(self, /) -> str:
        name = self.__class__.__name__
        input_value = {
            'options': self._entries,
            'parser': self._parser,
        }
        return f'{name}({input_value!r})'

    def get(self, key: str, /) -> ConfigEntry | None:
        return self._entries.get(key)

    def items(self, /) -> Iterable[tuple[str, ConfigEntry]]:
        return self._entries.items()

    def keys(self, /) -> Iterable[str]:
        return self._entries.keys()

    def values(self, /) -> Iterable[ConfigEntry]:
        return self._entries.values()

    @property
    def allow_unknown(self) -> bool:
        return self._parser['allowUnknown']

    @property
    def parse_parameters(self) -> bool:
        return self._parser['parseParameters']

    @property
    def aggregate_errors(self) -> bool:
        return self._parser['aggregateErrors']
