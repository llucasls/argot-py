import json
import tomllib
from typing import cast

from argot_cli.parser_config import ParserConfig
from argot_cli.argot_types import ParserConfigInput


def read_json_config(config_file: str) -> ParserConfig:
    """
    Read a configuration file in JSON format.

    The file is parsed as JSON and passed directly to the ParserConfig
    constructor. The resulting configuration is normalized and
    validated during construction.

    Args:
        config_file: Path to the JSON configuration file.

    Returns:
        A ParserConfig instance.

    Raises:
        OSError: if the file cannot be opened
        JSONDecodeError: if the file contains invalid JSON
        TypeError, ValueError: if the configuration is invalid
    """
    with open(config_file) as file:
        output = json.load(file)

    return ParserConfig(output)


def read_toml_config(config_file: str) -> ParserConfig:
    """
    Read a configuration file in TOML format.

    The file is parsed as TOML and the "entries" table is used as input
    to the ParserConfig constructor. The resulting configuration is
    normalized and validated during construction.

    Args:
        config_file: Path to the TOML configuration file.

    Returns:
        A ParserConfig instance.

    Raises:
        OSError: if the file cannot be opened
        TOMLDecodeError: if the file contains invalid TOML
        KeyError: if the "entries" table is not present
        TypeError, ValueError: if the configuration is invalid
    """
    with open(config_file, mode='rb') as file:
        result = tomllib.load(file)

    return ParserConfig(cast(ParserConfigInput, result))
