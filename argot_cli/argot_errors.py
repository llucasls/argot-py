class NullArgError(Exception):
    """
    Missing argument error.

    Raised when an option that requires an associated value is provided
    without one.

    If the option is an alias, the error message includes both the
    alias name and its target.
    """
    def __init__(self, name: str, target: str | None = None, **kwargs):
        msg: str
        if target is not None:
            msg = f"option '{name}' (alias for '{target}') must take an argument"
        else:
            msg = f"option '{name}' must take an argument"
        super().__init__(msg, **kwargs)


class NullIntError(Exception):
    """
    Missing integer argument error.

    Raised when an option of type "int" is provided without an
    associated value.

    This error does not cover invalid integer values. Conversion errors
    are raised separately by the underlying integer parsing logic.

    If the option is an alias, the error message includes both the
    alias name and its target.
    """
    def __init__(self, name: str, target: str | None = None, **kwargs):
        msg: str
        if target is not None:
            msg = f"option '{name}' (alias for '{target}') requires a numeric argument"
        else:
            msg = f"option '{name}' requires a numeric argument"
        super().__init__(msg, **kwargs)


class InvalidIntError(Exception): ...
