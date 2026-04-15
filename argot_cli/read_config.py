import json

import tomllib

from argot_cli.argot_types import ParserConfig


def read_json_config(config_file: str) -> ParserConfig:
    with open(config_file) as file:
        output = json.load(file)

    return ParserConfig(output)


def read_toml_config(config_file: str) -> ParserConfig:
    with open(config_file, mode='rb') as file:
        result = tomllib.load(file)

    return ParserConfig(result['entries'])
