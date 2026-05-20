from tests import TestCase

from argot_cli.argot_errors import (
    InvalidFloatError,
    InvalidIntError,
    NullArgError,
    NullFloatError,
    NullIntError,
    UnknownOptionError,
    InvalidOptionTypeError,
    AliasTargetNotFoundError,
    InvalidAliasTargetError,
    MissingOptionPropertyError,
    MissingOptionTypeError,
)


class TestErrors(TestCase):
    def test_invalid_int_error(self) -> None:
        value: str = ' 40 '
        error = InvalidIntError(value)
        self.assertEqual(error.value, value)
        with self.assertRaises(InvalidIntError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "' 40 ' is not a valid integer"
        )

    def test_invalid_float_error(self) -> None:
        value: str = ' 40 '
        error = InvalidFloatError(value)
        self.assertEqual(error.value, value)
        with self.assertRaises(InvalidFloatError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "' 40 ' is not a valid number"
        )

    def test_null_arg_error(self) -> None:
        option: str
        target: str

        option = 'j'
        error = NullArgError(option)
        self.assertEqual(error.option, option)
        self.assertIsNone(error.target)
        with self.assertRaises(NullArgError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "option 'j' must take an argument"
        )

        option = 't'
        target = 'tasks'
        error = NullArgError(option, target)
        self.assertEqual(error.option, option)
        self.assertEqual(error.target, target)
        with self.assertRaises(NullArgError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "option 't' (alias for 'tasks') must take an argument"
        )

    def test_null_int_error(self) -> None:
        option: str
        target: str

        option = 'i'
        error = NullIntError(option)
        self.assertEqual(error.option, option)
        self.assertIsNone(error.target)
        with self.assertRaises(NullIntError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "option 'i' requires an integer argument"
        )

        option = 'M'
        target = 'max'
        error = NullIntError(option, target)
        self.assertEqual(error.option, option)
        self.assertEqual(error.target, target)
        with self.assertRaises(NullIntError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "option 'M' (alias for 'max') requires an integer argument"
        )

    def test_null_float_error(self) -> None:
        option: str
        target: str

        option = 'f'
        error = NullFloatError(option)
        self.assertEqual(error.option, option)
        self.assertIsNone(error.target)
        with self.assertRaises(NullFloatError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "option 'f' requires a numeric argument"
        )

        option = 'M'
        target = 'max'
        error = NullFloatError(option, target)
        self.assertEqual(error.option, option)
        self.assertEqual(error.target, target)
        with self.assertRaises(NullFloatError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "option 'M' (alias for 'max') requires a numeric argument"
        )

    def test_unknown_option_error(self) -> None:
        option: str = 'x'
        error = UnknownOptionError(option)
        self.assertEqual(error.option, option)
        with self.assertRaises(UnknownOptionError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "option 'x' is not supported"
        )

    def test_invalid_option_type_error(self) -> None:
        tag: str = 'number'
        error = InvalidOptionTypeError(tag)
        self.assertEqual(error.type, tag)
        with self.assertRaises(InvalidOptionTypeError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "option type 'number' is not supported"
        )

    def test_alias_target_not_found_error(self) -> None:
        option: str = 'x'
        target: str = 'xtrace'
        error = AliasTargetNotFoundError(option, target)
        self.assertEqual(error.option, option)
        self.assertEqual(error.target, target)
        with self.assertRaises(AliasTargetNotFoundError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "target value 'xtrace' for option 'x' was not found"
        )

    def test_invalid_alias_target_error(self) -> None:
        option: str = 'L'
        target: str = 'l'
        error = InvalidAliasTargetError(option, target)
        self.assertEqual(error.option, option)
        self.assertEqual(error.target, target)
        with self.assertRaises(InvalidAliasTargetError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "cannot create an alias to another alias (L => l)"
        )

    def test_missing_option_property_error(self) -> None:
        option: str = 'n'
        prop: str = 'target'
        error = MissingOptionPropertyError(option, prop)
        self.assertEqual(error.option, option)
        self.assertEqual(error.property, prop)
        with self.assertRaises(MissingOptionPropertyError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "option 'n' is missing required property 'target'"
        )

    def test_missing_option_type_error(self) -> None:
        option: str = 'dry-run'
        error = MissingOptionTypeError(option)
        self.assertEqual(error.option, option)
        with self.assertRaises(MissingOptionTypeError) as cm:
            raise error
        self.assertEqual(
            cm.exception.args[0],
            "option 'dry-run' is missing required property 'type'"
        )
