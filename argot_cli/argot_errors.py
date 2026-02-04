class NullArgError(Exception):
    def __init__(self, name: str, target: str | None = None, **kwargs):
        msg: str
        if target is not None:
            msg = f"option '{name}' (alias for '{target}') must take an argument"
        else:
            msg = f"option '{name}' must take an argument"
        super().__init__(msg, **kwargs)


class NullIntError(Exception):
    def __init__(self, name: str, target: str | None = None, **kwargs):
        msg: str
        if target is not None:
            msg = f"option '{name}' (alias for '{target}') requires a numeric argument"
        else:
            msg = f"option '{name}' requires a numeric argument"
        super().__init__(msg, **kwargs)
