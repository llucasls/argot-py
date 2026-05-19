"""
Argot CLI argument parser.

This module provides a schema-based command-line argument parser.
The parser processes an array of strings and produces a structured result
containing options, parameters, and operands.

Parsing behavior is fully determined by a configuration object.
"""
from importlib.metadata import version

from argot_cli.arg_parser import ArgParser
from argot_cli.read_config import read_json_config, read_toml_config
from argot_cli.argot_types import ConfigEntry, ConfigEntries
from argot_cli.parser_config import ParserConfig


__all__ = [
    "ArgParser",
    "ParserConfig",
    "read_json_config",
    "read_toml_config",
    "ConfigEntry",
    "ConfigEntries",
    "__version__",
]


__version__: str | None
try:
    __version__ = version("argot_cli")
except ModuleNotFoundError:
    __version__ = None
