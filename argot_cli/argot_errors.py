class ConfigError(Exception):
    """
    Configuration error.
    Represents errors caused by an invalid parser configuration.
    These errors occur when defining or initializing the parser,
    such as using unsupported option types or referencing invalid
    alias targets.
    Configuration errors are independent of user input and are
    typically raised before any parsing takes place.
    """


class InvalidIntError(RuntimeError):
    """
    Invalid integer argument error.
    Raised when an option of type "int" is provided with an associated
    value that cannot be parsed as an integer.
    This error only applies when a value is present. Missing values are
    reported using NullIntError.
    """
    __slots__ = ['_value']

    def __init__(self, value: str):
        super().__init__(f"'{value}' is not a valid integer")
        self._value = value

    @property
    def value(self) -> str:
        return self._value


class NullArgError(RuntimeError):
    """
    Missing argument error.

    Raised when an option that requires an associated value is provided
    without one.

    If the option is an alias, the error message includes both the
    alias name and its target.
    """
    __slots__ = ['_option', '_target']

    def __init__(self, name: str, target: str | None = None):
        msg: str
        if target is not None:
            msg = f"option '{name}' (alias for '{target}') must take an argument"
        else:
            msg = f"option '{name}' must take an argument"
        super().__init__(msg)

        self._option = name
        self._target = target

    @property
    def option(self) -> str:
        return self._option

    @property
    def target(self) -> str | None:
        return self._target


class NullIntError(RuntimeError):
    """
    Missing integer argument error.

    Raised when an option of type "int" is provided without an
    associated value.

    This error does not cover invalid integer values. Conversion errors
    are raised separately by the underlying integer parsing logic.

    If the option is an alias, the error message includes both the
    alias name and its target.
    """
    __slots__ = ['_option', '_target']

    def __init__(self, name: str, target: str | None = None):
        msg: str
        if target is not None:
            msg = f"option '{name}' (alias for '{target}') requires a numeric argument"
        else:
            msg = f"option '{name}' requires a numeric argument"
        super().__init__(msg)

        self._option = name
        self._target = target

    @property
    def option(self) -> str:
        return self._option

    @property
    def target(self) -> str | None:
        return self._target


class UnknownOptionError(RuntimeError):
    """
    Unknown option error.
    Raised when an input contains an option that is not defined in the
    parser configuration.
    This applies to both long and short options. The error is triggered
    as soon as the parser encounters an unrecognized option name.
    """
    __slots__ = ['_option']

    def __init__(self, name: str):
        super().__init__(f"option '{name}' is not supported")
        self._option = name

    @property
    def option(self) -> str:
        return self._option


class InvalidOptionTypeError(ConfigError):
    """
    Invalid option type error.
    Raised when an option is declared with a type that is not supported
    by the parser.
    """
    __slots__ = ['_type']

    def __init__(self, tag: str):
        super().__init__(f"option type '{tag}' is not supported")
        self._type = tag

    @property
    def type(self) -> str:
        return self._type


class AliasTargetNotFoundError(ConfigError):
    """
    Alias target not found error.
    Raised when an alias references a target option that does not exist
    in the parser configuration.
    This is a configuration error and indicates that the alias points
    to an undefined option.
    """
    __slots__ = ['_option', '_target']

    def __init__(self, name: str, target: str):
        super().__init__(f"target value '{target}' for option '{name}' was not found")
        self._option = name
        self._target = target

    @property
    def option(self) -> str:
        return self._option

    @property
    def target(self) -> str:
        return self._target


class InvalidAliasTargetError(ConfigError):
    """
    Invalid alias target error.
    Raised when an alias references a target that is not a valid option
    for aliasing.
    This may occur if the target is itself an alias (when alias chaining
    is not supported) or if the target cannot accept the alias due to
    type or configuration constraints.
    """
    __slots__ = ['_option', '_target']

    def __init__(self, name: str, target: str):
        super().__init__(f'cannot create an alias to another alias ({name} => {target})')
        self._option = name
        self._target = target

    @property
    def option(self) -> str:
        return self._option

    @property
    def target(self) -> str:
        return self._target


class MissingOptionPropertyError(ConfigError):
    """
    Missing option property error.
    Raised when an option entry in the parser configuration is missing
    one or more required properties.
    This is a configuration error and indicates that the option
    definition is incomplete or malformed.
    Implementations may include the option name and the missing
    property name to aid debugging.
    """
    __slots__ = ['_option', '_property']

    def __init__(self, name: str, prop: str):
        super().__init__(f"option '{name}' is missing required property '{prop}'")
        self._option = name
        self._property = prop

    @property
    def option(self) -> str:
        return self._option

    @property
    def property(self) -> str:
        return self._property


class MissingOptionTypeError(ConfigError):
    """
    Missing option type error.
    Raised when a configuration entry does not define a "type" property.
    The "type" property is required for all option entries and determines
    how the option is parsed and validated. Without it, the entry cannot
    be interpreted by the parser.
    This is a configuration error and is typically raised during
    configuration validation.
    """
    __slots__ = ['_option']

    def __init__(self, name: str):
        super().__init__(f"option '{name}' is missing required property 'type'")
        self._option = name

    @property
    def option(self) -> str:
        return self._option
