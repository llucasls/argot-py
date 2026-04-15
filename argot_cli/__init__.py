from importlib.metadata import version

from argot_cli.arg_parser import ArgParser
from argot_cli.read_config import read_json_config, read_toml_config
from argot_cli.argot_types import ConfigEntry, LabeledEntry, ParserConfig


__all__ = [
    "ArgParser",
    "read_json_config",
    "read_toml_config",
    "ConfigEntry",
    "LabeledEntry",
    "ParserConfig"
    "__version__",
]


__version__: str | None
try:
    __version__ = version("argot_cli")
except ModuleNotFoundError:
    __version__ = None
