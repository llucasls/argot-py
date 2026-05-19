from tests import TestCase

from argot_cli.read_config import read_json_config, read_toml_config
from argot_cli.parser_config import ParserConfig


class TestReadJSONConfig(TestCase):
    def test_return_parser_config_object_from_json_map(self):
        file = 'tests/config_map.json'
        parser_config = read_json_config(file)

        self.assertIsInstance(parser_config, ParserConfig)


class TestReadTOMLConfig(TestCase):
    def test_return_parser_config_object_from_toml_map(self):
        file = 'tests/config_map.toml'
        parser_config = read_toml_config(file)

        self.assertIsInstance(parser_config, ParserConfig)
