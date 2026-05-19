from tests import TestCase

from argot_cli.parser_config import ParserConfig
from argot_cli.argot_errors import InvalidAliasTargetError


class TestParserConfig(TestCase):
    def test_create_parser_config_from_object(self):
        parser_config = ParserConfig({
            'quiet': {'type': 'flag'},
            'output': {'type': 'text'},
        })

        self.assertIsInstance(parser_config, ParserConfig)
        self.assertDictMatch(parser_config.get('quiet'), {'type': 'flag'})
        self.assertDictMatch(parser_config.get('output'), {'type': 'text'})

    def test_raise_error_on_invalid_input(self):
        with self.assertRaises(TypeError):
            ParserConfig(None)

    def test_raise_error_on_alias_chains(self):
        with self.assertRaises(InvalidAliasTargetError):
            ParserConfig({
                'version': {'type': 'int'},
                'v': {'type': 'alias', 'target': 'version'},
                'V': {'type': 'alias', 'target': 'v'},
            })

    def test_read_properties_from_parser_config_object(self):
        parser_config = ParserConfig({
            'output': {'type': 'text'},
            'users': {'type': 'list'},
            'logLevel': {'type': 'count'},
            'workers': {'type': 'int'},
        })

        self.assertEqual(len(parser_config), 4)
        self.assertTrue('output' in parser_config)
        self.assertTrue('logLevel' in parser_config)
        self.assertFalse('quiet' in parser_config)

    def test_iterate_over_keys(self):
        parser_config = ParserConfig({
            'output': {'type': 'text'},
            'users': {'type': 'list'},
            'logLevel': {'type': 'count'},
            'workers': {'type': 'int'},
        })

        for key in parser_config.keys():
            self.assertIsInstance(key, str)
            self.assertTrue(key in parser_config)

    def test_iterate_over_values(self):
        parser_config = ParserConfig({
            'output': {'type': 'text'},
            'users': {'type': 'list'},
            'logLevel': {'type': 'count'},
            'workers': {'type': 'int'},
        })

        for value in parser_config.values():
            self.assertTrue('type' in value)
            self.assertIsInstance(value['type'], str)

    def test_iterate_over_items(self):
        parser_config = ParserConfig({
            'output': {'type': 'text'},
            'users': {'type': 'list'},
            'logLevel': {'type': 'count'},
            'workers': {'type': 'int'},
        })

        for key, value in parser_config.items():
            self.assertIsInstance(key, str)
            self.assertTrue(key in parser_config)

            self.assertTrue('type' in value)
            self.assertIsInstance(value['type'], str)

            self.assertEqual(parser_config[key], value)

    def test_return_object_string_representation(self):
        parser_config = ParserConfig({
            'output': {'type': 'text'},
            'users': {'type': 'list'},
            'logLevel': {'type': 'count'},
            'workers': {'type': 'int'},
        })
        self.assertEqual(
            repr(parser_config),
            "ParserConfig({'output': {'type': 'text'}, 'users': {'type': 'list'}, 'logLevel': {'type': 'count'}, 'workers': {'type': 'int'}})"
        )

    def test_return_correct_number_of_entries(self):
        config_obj = {
            'output': {'type': 'text'},
            'users': {'type': 'list'},
            'logLevel': {'type': 'count'},
            'workers': {'type': 'int'},
        }
        parser_config = ParserConfig(config_obj)

        self.assertEqual(len(parser_config), len(config_obj))
