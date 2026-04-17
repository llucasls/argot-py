from typing import cast

import argot_cli.argot_types as t

def validate_entry(entry: t.LabeledEntry) -> None:
    """
    Validate a single configuration entry.

    The entry must be a mapping containing at least the keys "option"
    and "type".  Additional constraints depend on the option type:

    - flag, count: no additional fields are required
    - text: "default", if present, must be a string
    - int: "default", if present, must be an integer
    - list: "sep", if present, must be a string
    - alias: must define "target" as a string

    Raises:
        TypeError: if a value has an invalid type or the option type is
        unsupported
        ValueError: if required fields are missing
    """
    if not isinstance(entry, dict):
        raise TypeError('option config entry must be a dictionary')

    for key in ['option', 'type']:
        if key not in entry:
            raise ValueError(f"'{key}' not found in config entry")

    tag: t.OptionType = entry['type']

    match tag:
        case t.OptionType.FLAG:
            pass
        case t.OptionType.COUNT:
            pass
        case t.OptionType.TEXT:
            default = entry.get('default')
            if default is not None and not isinstance(default, str):
                raise TypeError('default value must be a string')
        case t.OptionType.INT:
            default = entry.get('default')
            if default is not None and not isinstance(default, int):
                raise TypeError('default value must be an integer')
        case t.OptionType.LIST:
            sep = entry.get('sep')
            if sep is not None and not isinstance(sep, str):
                raise TypeError('sep value must be a string')
        case t.OptionType.ALIAS:
            if 'target' not in entry:
                option = entry['option']
                msg = f"'target' not found in alias option {option}"
                raise ValueError(msg)
            if not isinstance(cast(t.AliasEntry, entry)['target'], str):
                raise TypeError('target value must be a string')
        case _:
            raise TypeError(f"option type '{tag}' is not supported")


def validate_entries(entries: dict[str, t.ConfigEntry]) -> None:
    """
    Validate a mapping of configuration entries.

    Each entry is validated individually. In addition, alias options
    are checked to ensure their target refers to an existing option.

    Raises:
        TypeError: if an entry contains invalid types
        ValueError: if validation fails or an alias target is not found
    """
    aliases: list[tuple[str, str]] = []

    for option, config in entries.items():
        entry = cast(t.LabeledEntry, {'option': option, **config})
        validate_entry(entry)
        tag: t.OptionType = entry['type']

        if tag == t.OptionType.ALIAS:
            target = cast(t.AliasEntry, entry)['target']
            aliases.append((option, target))

    for name, target in aliases:
        if target not in entries:
            msg = f"target value '{target}' for option '{name}' was not found"
            raise ValueError(msg)
