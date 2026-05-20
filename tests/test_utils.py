from tests import TestCase
from typing import cast

from argot_cli.argot_utils import (
    parse_int,
    parse_float,
    validate_entry,
    validate_entries,
    validate_entries_aggregate,
)
from argot_cli.argot_types import ConfigEntries, ConfigEntry
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


class TestParseInt(TestCase):
    def test_return_int(self):
        self.assertEqual(parse_int("212"), 212)
        self.assertEqual(parse_int("-1"), -1)
        self.assertEqual(parse_int("49"), 49)
        self.assertEqual(parse_int("18446744073709551615"), 18446744073709551615)

    def test_raise_error(self):
        with self.assertRaises(InvalidIntError) as cm:
            parse_int("0xf2")
        self.assertEqual(
            cm.exception.args[0],
            "'0xf2' is not a valid integer"
        )
        with self.assertRaises(InvalidIntError) as cm:
            parse_int("	2 ")
        self.assertEqual(
            cm.exception.args[0],
            "'	2 ' is not a valid integer"
        )


class TestParseFloat(TestCase):
    def test_return_float(self):
        self.assertEqual(parse_float('212'), 212.0)
        self.assertEqual(parse_float('-12'), -12.0)
        self.assertEqual(parse_float('.25'), 0.25)
        self.assertEqual(parse_float('1e6'), 1_000_000.0)

    def test_raise_error(self):
        with self.assertRaises(InvalidFloatError) as cm:
            parse_float("	2 ")
        self.assertEqual(
            cm.exception.args[0],
            "'	2 ' is not a valid number"
        )
        with self.assertRaises(InvalidFloatError) as cm:
            parse_float('NaN')
        with self.assertRaises(InvalidFloatError) as cm:
            parse_float('Infinity')


class TestValidateEntry(TestCase):
    def test_raise_error_on_null_entry(self):
        with self.assertRaises(TypeError) as cm:
            validate_entry('z', None)
        self.assertEqual(
            cm.exception.args[0],
            'option config entry must be a dictionary'
        )

    def test_raise_error_on_non_object_input(self):
        with self.assertRaises(TypeError) as cm:
            validate_entry('n', 4)
        self.assertEqual(
            cm.exception.args[0],
            'option config entry must be a dictionary'
        )

    def test_raise_error_if_entry_does_not_have_type(self):
        with self.assertRaises(MissingOptionTypeError) as cm:
            validate_entry('a', {'target': 'x'})
        self.assertEqual(
            cm.exception.args[0],
            "option 'a' is missing required property 'type'"
        )

    def test_raise_error_if_text_default_value_is_not_a_string(self):
        entry = {'type': 'text', 'default': ['config.json']}
        with self.assertRaises(TypeError) as cm:
            validate_entry('file', entry)
        self.assertEqual(
            cm.exception.args[0],
            "default value must be a string"
        )

    def test_raise_error_if_int_default_value_is_not_an_integer(self):
        entry = {'type': 'int', 'default': 12.5}
        with self.assertRaises(TypeError) as cm:
            validate_entry('jobs', entry)
        self.assertEqual(
            cm.exception.args[0],
            "default value must be an integer"
        )

    def test_raise_error_if_float_default_value_is_not_a_float(self):
        entry = {'type': 'float', 'default': '12.5'}
        with self.assertRaises(TypeError) as cm:
            validate_entry('jobs', entry)
        self.assertEqual(
            cm.exception.args[0],
            "default value must be a number"
        )

    def test_raise_error_if_list_sep_value_is_not_a_string(self):
        entry = {'type': 'list', 'sep': 33}
        with self.assertRaises(TypeError) as cm:
            validate_entry('tasks', entry)
        self.assertEqual(
            cm.exception.args[0],
            "sep value must be a string"
        )

    def test_raise_error_on_alias_without_a_target(self):
        entry = {'type': 'alias'}
        with self.assertRaises(MissingOptionPropertyError) as cm:
            validate_entry('u', entry)
        self.assertEqual(
            cm.exception.args[0],
            "option 'u' is missing required property 'target'"
        )

    def test_raise_error_if_alias_target_value_is_not_a_string(self):
        entry = {'type': 'alias', 'target': 7}
        with self.assertRaises(TypeError) as cm:
            validate_entry('v', entry)
        self.assertEqual(
            cm.exception.args[0],
            'target value must be a string'
        )

    def test_raise_error_on_unknown_type(self):
        entry = {'type': 'string'}
        with self.assertRaises(InvalidOptionTypeError) as cm:
            validate_entry('version', entry)
        self.assertEqual(
            cm.exception.args[0],
            f"option type 'string' is not supported"
        )


class TestValidateEntries(TestCase):
    def test_do_not_throw_on_valid_entries(self) -> None:
        entries: ConfigEntries = {
            'strict': { 'type': 'flag' },
            'output': { 'type': 'text' },
            'logFile': { 'type': 'text', 'default': 'access.log' },
            'retries': { 'type': 'int' },
            'threads': { 'type': 'int', 'default': 0 },
            'logLevel': { 'type': 'count' },
            'tasks': { 'type': 'list' },
            'path': { 'type': 'list', 'sep': ':' },
            'v': { 'type': 'alias', 'target': 'logLevel' },
            's': { 'type': 'alias', 'target': 'strict' },
            'o': { 'type': 'alias', 'target': 'output' },
        }
        validate_entries(entries)

    def test_raise_error_if_target_option_is_not_found(self) -> None:
        entries: ConfigEntries = {
            's': { 'type': 'alias', 'target': 'strict' },
            'notStrict': { 'type': 'flag' },
        }
        with self.assertRaises(AliasTargetNotFoundError) as cm:
            validate_entries(entries)
        self.assertIsInstance(cm.exception, AliasTargetNotFoundError)

    def test_raise_error_on_alias_to_another_alias(self) -> None:
        entries: ConfigEntries = {
            'list': {'type': 'flag'},
            'l': {'type': 'alias', 'target': 'list'},
            'L': {'type': 'alias', 'target': 'l'},
        }
        with self.assertRaises(InvalidAliasTargetError):
            validate_entries(entries)


class TestValidateEntriesAggregate(TestCase):
    def test_do_not_throw_on_valid_entries(self) -> None:
        entries: ConfigEntries = {
            'strict': { 'type': 'flag' },
            'output': { 'type': 'text' },
            'logFile': { 'type': 'text', 'default': 'access.log' },
            'retries': { 'type': 'int' },
            'threads': { 'type': 'int', 'default': 0 },
            'logLevel': { 'type': 'count' },
            'tasks': { 'type': 'list' },
            'path': { 'type': 'list', 'sep': ':' },
            'v': { 'type': 'alias', 'target': 'logLevel' },
            's': { 'type': 'alias', 'target': 'strict' },
            'o': { 'type': 'alias', 'target': 'output' },
        }
        validate_entries_aggregate(entries)

    def test_raise_aggregate_error(self) -> None:
        entries = cast(ConfigEntries, {
            'o': {'type': 'string'},
            'i': {'type': 'number'},
            's': {'type': 'alias', 'target': 'strict'},
            'notStrict': {'type': 'flag'},
            'list': {'type': 'flag'},
            'l': {'type': 'alias', 'target': 'list'},
            'L': {'type': 'alias', 'target': 'l'},
        })
        with self.assertRaises(ConfigError) as cm:
            validate_entries_aggregate(entries)
        error = cm.exception
        self.assertEqual(len(error.errors), 4)
        self.assertIsInstance(error.errors[0], InvalidOptionTypeError) # type string
        self.assertIsInstance(error.errors[1], InvalidOptionTypeError) # type number
        self.assertIsInstance(error.errors[2], AliasTargetNotFoundError) # target strict
        self.assertIsInstance(error.errors[3], InvalidAliasTargetError) # target l
