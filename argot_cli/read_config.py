import json
from typing import cast

import tomllib

from argot_cli.argot_types import ConfigEntry, LabeledEntry, OptionType
from argot_cli.argot_utils import validate_entries


type EntryList = list[LabeledEntry]
type EntryMap = dict[str, ConfigEntry]
type Entries = EntryList | EntryMap


def read_json_config(config_file: str) -> EntryMap:
    with open(config_file) as file:
        output = json.load(file)

    return normalize_entries(output)


def read_toml_config(config_file: str) -> EntryMap:
    with open(config_file, mode='rb') as file:
        result = tomllib.load(file)

    return normalize_entries(result['entries'])


def normalize_entries(entry_list: Entries) -> EntryMap:
    if not isinstance(entry_list, (list, dict)):
        raise TypeError('input value must be a dictionary or a list')

    output: EntryMap = {}

    dict_entry: ConfigEntry
    if isinstance(entry_list, dict):
        for name, dict_entry in entry_list.items():
            if dict_entry is None:
                raise TypeError('entry cannot be null')
            if not isinstance(dict_entry, dict):
                raise TypeError('entry must be a dictionary')
            if 'type' not in dict_entry:
                raise TypeError('config entry missing "type"')

            output[name] = dict_entry

    labeled_entry: LabeledEntry
    if isinstance(entry_list, list):
        for labeled_entry in entry_list:
            if labeled_entry is None:
                raise TypeError('entry cannot be null')
            if not isinstance(labeled_entry, dict):
                raise TypeError('entry must be a dictionary')
            if 'type' not in labeled_entry:
                raise TypeError('config entry missing "type"')

            option = labeled_entry['option']
            output[option] = {}
            for key, value in labeled_entry.items():
                if key == 'option':
                    continue
                else:
                    cast(dict, output[option])[key] = value

    def hook(pairs):
        output = {}
        for key, value in pairs:
            if key == 'type':
                output['type'] = OptionType(value)
            else:
                output[key] = value
        return output

    validate_entries(output)

    return output
