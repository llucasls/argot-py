import re
from typing import cast

import argot_cli.argot_types as t
from argot_cli.argot_errors import (
    AliasTargetNotFoundError,
    ConfigError,
    InvalidFloatError,
    InvalidIntError,
    InvalidAliasTargetError,
    InvalidOptionTypeError,
    MissingOptionTypeError,
    MissingOptionPropertyError,
)


INT_RE = re.compile(r'^(-|\+)?\d+$')
FLOAT_RE = re.compile(r'^(-|\+)?(\d+(\.\d+)?|\.\d+)([eE](-|\+)?\d+)?$')


def parse_int(value: str) -> int:
    """Parse a string with an integer numeric value."""

    if not INT_RE.match(value):
        raise InvalidIntError(value)
    return int(value)


def parse_float(value: str) -> float:
    """Parse a string with a floating-point numeric value."""

    if not FLOAT_RE.match(value):
        raise InvalidFloatError(value)
    return float(value)


def validate_entry(name: str, entry: t.ConfigEntry) -> None:
    """
    Validate a single configuration entry.

    The entry must be a mapping containing at least the keys "option"
    and "type".  Additional constraints depend on the option type:

    - flag, count: no additional fields are required
    - text: "default", if present, must be a string
    - int: "default", if present, must be an integer
    - float: "default", if present, must be a number
    - list: "sep", if present, must be a string
    - alias: must define "target" as a string

    Raises:
        TypeError: if a value has an invalid type or the option type is
        unsupported

        ValueError: if required fields are missing

        MissingOptionPropertyError: if a required property is missing
        InvalidOptionTypeError: if the option type is not supported
    """
    if not isinstance(entry, dict):
        raise TypeError('option config entry must be a dictionary')
    elif 'type' not in entry:
        raise MissingOptionTypeError(name)

    tag: str = entry['type']

    match tag:
        case 'flag' | 'count':
            pass
        case 'text':
            default = entry.get('default')
            if default is not None and not isinstance(default, str):
                raise TypeError('default value must be a string')
        case 'int':
            default = entry.get('default')
            if default is not None and not isinstance(default, int):
                raise TypeError('default value must be an integer')
        case 'float':
            default = entry.get('default')
            if default is not None and not isinstance(default, (float, int)):
                raise TypeError('default value must be a number')
        case 'list':
            sep = entry.get('sep')
            if sep is not None and not isinstance(sep, str):
                raise TypeError('sep value must be a string')
        case 'alias':
            if 'target' not in entry:
                raise MissingOptionPropertyError(name, 'target')

            target = entry.get('target')
            if not isinstance(target, str):
                raise TypeError('target value must be a string')
        case _:
            raise InvalidOptionTypeError(tag)


def validate_entries(entries: t.ConfigEntries) -> None:
    """
    Validate a mapping of configuration entries.

    Each entry is validated individually. In addition, alias options
    are checked to ensure their target refers to an existing option.

    Raises:
        TypeError: if an entry contains invalid types
        AliasTargetNotFoundError: if an alias target does not exist
        is not found
        InvalidAliasTargetError: if an alias targets another alias
    """
    aliases: list[tuple[str, str]] = []

    for name, entry in entries.items():
        validate_entry(name, entry)
        tag: str = entry['type']

        if tag == 'alias':
            target = cast(t.AliasEntry, entry)['target']
            aliases.append((name, target))

    for name, target in aliases:
        if target not in entries:
            raise AliasTargetNotFoundError(name, target)
        target_entry = entries[target]
        if target_entry['type'] == 'alias':
            raise InvalidAliasTargetError(name, target)


def validate_entries_aggregate(entries: t.ConfigEntries) -> None:
    aliases: list[tuple[str, str]] = []
    error = ConfigError('parser configuration is not valid')

    for name, entry in entries.items():
        try:
            validate_entry(name, entry)
        except Exception as err:
            error.append(err)
            continue
        tag: t.OptionType = entry['type']
        if tag == 'alias':
            target = cast(t.AliasEntry, entry)['target']
            aliases.append((name, target))

    for name, target in aliases:
        if target not in entries:
            error.append(AliasTargetNotFoundError(name, target))
            continue
        target_entry: t.ConfigEntry = entries[target]
        if target_entry['type'] == 'alias':
            error.append(InvalidAliasTargetError(name, target))

    if len(error.errors) == 1:
        raise error.errors[0]
    elif len(error.errors) > 1:
        raise error
