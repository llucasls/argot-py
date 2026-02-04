from abc import ABCMeta
import re
from typing import cast, Final, TypedDict

import argot_cli.argot_types as t
from argot_cli.argot_errors import NullArgError, NullIntError


class ArgParserResult[K, V](dict[K, V], metaclass=ABCMeta):
    __slots__ = ('_frozen',)
    _frozen: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._frozen = False

    def __setitem__(self, key: K, value: V, /):
        if self._frozen:
            raise TypeError('you cannot modify option values')
        super().__setitem__(key, value)

    def __delitem__(self, key: K, /):
        if self._frozen:
            raise TypeError('you cannot delete parsed options')
        super().__delitem__(key)

    def clear(self, /):
        if self._frozen:
            raise TypeError('you cannot delete parsed options')
        super().clear()

    def pop(self, key: K, /, *args) -> V:
        if self._frozen:
            raise TypeError('you cannot delete parsed options')
        return super().pop(key, *args)

    def popitem(self, /) -> tuple[K, V]:
        if self._frozen:
            raise TypeError('you cannot delete parsed options')
        return super().popitem()

    def setdefault(self, key: K, default=None, /) -> V:
        if self._frozen:
            raise TypeError('you cannot modify option values')
        return super().setdefault(key, default)

    def _freeze(self):
        self._frozen = True


class Options(ArgParserResult[str, t.OptionValue]):
    """short options and GNU-style long optons"""
    __slots__ = ()


class Parameters(ArgParserResult[str, str]):
    """name=value variable assignments"""
    __slots__ = ()


class Operands(list[str]):
    """command-line positional arguments"""
    __slots__ = ()


class ParseResult(TypedDict):
    options: Options
    parameters: Parameters
    operands: Operands


class ArgParser:
    long_opt_exp = re.compile(r'^--')
    short_opt_exp = re.compile(r'^-[^-]')
    assignment_exp = re.compile(r'^--([^=]+)=(.+)?')
    parameter_exp = re.compile(r'^([^=]+)=(.+)?')
    _configs: dict[str, t.ConfigEntry]
    __slots__ = ('_configs',)

    def __init__(self, configs: dict[str, t.ConfigEntry], /):
        self._configs = configs

    def parse(self, arg_list: list[str], /) -> ParseResult:
        options = Options()
        parameters = Parameters()
        operands = Operands()

        if not isinstance(arg_list, list):
            raise TypeError('arg_list must be a list of strings')

        stop_parsing = False

        n: Final[int] = len(arg_list)
        i = 0

        old_value: t.OptionValue
        new_value: t.OptionValue
        match_parameter: re.Match | None
        next_arg: str | None
        while i < n:
            arg = arg_list[i]

            if stop_parsing:
                operands.append(arg)
                i += 1
                continue

            if arg == '--':
                stop_parsing = True
                i += 1
                continue

            match_parameter = self.parameter_exp.match(arg)
            if self.long_opt_exp.match(arg):
                name, new_value = self._parse_long_option(arg)
                options[name] = new_value
            elif self.short_opt_exp.match(arg):
                try:
                    next_arg = arg_list[i+1]
                except IndexError:
                    next_arg = None
                should_skip, pairs = self._parse_short_option(arg, next_arg)
                for name, value in pairs.items():
                    if self._configs[name]['type'] == t.OptionType.COUNT:
                        old_value = cast(int, options.get(name, 0))
                        new_value = cast(int, value)
                        options[name] = old_value + new_value
                    elif self._configs[name]['type'] == t.OptionType.LIST:
                        old_value = cast(list[str], options.get(name, []))
                        new_value = cast(list[str], value)
                        old_value.extend(new_value)
                        options[name] = old_value
                    else:
                        options[name] = value
                    if should_skip:
                        i += 1
            elif match_parameter is not None:
                name, value = match_parameter.groups()
                parameters[name] = value if value is not None else ''
            else:
                operands.append(arg)

            i += 1

        options._freeze()
        parameters._freeze()
        return {
            'options': options,
            'parameters': parameters,
            'operands': operands,
        }

    def _parse_long_option(self, arg: str) -> tuple[str, t.OptionValue]:
        offset: Final[int] = 2

        name: str
        value: str | None
        try:
            match = cast(re.Match, self.assignment_exp.match(arg))
            _name, _value = match.groups()
            name = _name
            value = _value if _value is not None else ''
        except Exception:
            name = arg[2:]
            value = None

        entry: t.ConfigEntry = self._configs[name]
        tag: t.OptionType = entry['type']
        new_value: t.OptionValue

        match tag:
            case t.OptionType.FLAG:
                return (name, True)
            case t.OptionType.TEXT:
                if value is not None:
                    return (name, value)
                elif 'default' in entry:
                    new_value = cast(t.TextEntry, entry)['default']
                    return (name, new_value)

                raise NullArgError(name)
            case t.OptionType.INT:
                if value is not None and value != '':
                    return (name, int(value))
                elif 'default' in entry:
                    new_value = cast(t.IntEntry, entry)['default']
                    return (name, new_value)

                raise NullIntError(name)
            case t.OptionType.COUNT:
                if value is not None:
                    return (name, int(value))
                return (name, 1)
            case t.OptionType.LIST:
                if value == '':
                    return (name, [])
                elif value is not None:
                    sep = cast(t.ListEntry, entry).get('sep', ',')
                    return (name, value.split(sep))

                raise NullArgError(name)
            case t.OptionType.ALIAS:
                target = cast(t.AliasEntry, entry)['target']
                target_entry: t.ConfigEntry = self._configs[target]
                target_type: t.OptionType = target_entry['type']

                match target_type:
                    case t.OptionType.FLAG:
                        return (target, True)
                    case t.OptionType.TEXT:
                        if value is not None:
                            return (target, value)
                        elif 'default' in target_entry:
                            new_value = cast(t.TextEntry, target_entry)['default']
                            return (target, new_value)

                        raise NullArgError(name, target)
                    case t.OptionType.INT:
                        if value is not None and value != '':
                            return (target, int(value))
                        elif 'default' in target_entry:
                            new_value = cast(t.IntEntry, target_entry)['default']
                            return (target, new_value)

                        raise NullIntError(name, target)
                    case t.OptionType.COUNT:
                        if value is not None:
                            return (target, int(value))
                        return (target, 1)
                    case t.OptionType.LIST:
                        if value == '':
                            return (target, [])
                        elif value is not None:
                            sep = cast(t.ListEntry, target_entry).get('sep', ',')
                            return (target, value.split(sep))

                        raise NullArgError(name, target)
                    case _:
                        msg = f"type '{target_type}' is not supported"
                        raise TypeError(msg)
            case _:
                raise TypeError(f"type '{tag}' is not supported")

    def _parse_short_option(
        self,
        arg: str,
        next_arg: str | None,
    ) -> tuple[bool, dict[str, t.OptionValue]]:
        name: str
        value: str | None
        entry: t.ConfigEntry

        pairs: dict[str, t.OptionValue] = {}

        i = 1
        n: Final[int] = len(arg)
        while i < n:
            name = arg[i]
            value = next_arg
            entry = self._configs[name]
            tag: t.OptionType = entry['type']
            default: str | int

            match tag:
                case t.OptionType.FLAG:
                    pairs[name] = True
                case t.OptionType.TEXT:
                    if i < n - 1:
                        value = arg[i + 1:n]
                        pairs[name] = value
                        return (False, pairs)
                    elif 'default' in entry:
                        default = cast(t.TextEntry, entry)['default']
                        pairs[name] = default
                        return (False, pairs)
                    elif value is not None:
                        pairs[name] = value
                        return (True, pairs)

                    raise NullArgError(name)
                case t.OptionType.INT:
                    if i < n - 1:
                        value = arg[i + 1:n]
                        pairs[name] = int(value)
                        return (False, pairs)
                    elif 'default' in entry:
                        default = cast(t.IntEntry, entry)['default']
                        pairs[name] = default
                        return (False, pairs)
                    elif value is not None:
                        pairs[name] = int(value)
                        return (True, pairs)

                    raise NullIntError(name)
                case t.OptionType.COUNT:
                    old_value = cast(int, pairs.get(name, 0))
                    pairs[name] = old_value + 1
                case t.OptionType.LIST:
                    if i < n - 1:
                        value = arg[i + 1:n]
                        sep = cast(t.ListEntry, entry).get('sep', ',')
                        pairs[name] = value.split(sep)
                        return (False, pairs)
                    elif value == '':
                        pairs[name] = []
                        return (True, pairs)
                    elif value is not None:
                        sep = cast(t.ListEntry, entry).get('sep', ',')
                        pairs[name] = value.split(sep)
                        return (True, pairs)

                    raise NullArgError(name)
                case t.OptionType.ALIAS:
                    target: str = cast(t.AliasEntry, entry)['target']
                    target_entry: t.ConfigEntry = self._configs[target]
                    target_type: t.OptionType = target_entry['type']

                    match target_type:
                        case t.OptionType.FLAG:
                            pairs[target] = True
                        case t.OptionType.TEXT:
                            if i < n - 1:
                                value = arg[i + 1:n]
                                pairs[target] = value
                                return (False, pairs)
                            elif 'default' in target_entry:
                                default = cast(t.TextEntry, target_entry)['default']
                                pairs[target] = default
                                return (False, pairs)
                            elif value is not None:
                                pairs[target] = value
                                return (True, pairs)

                            raise NullArgError(name, target)
                        case t.OptionType.INT:
                            if i < n - 1:
                                value = arg[i + 1:n]
                                pairs[target] = int(value)
                                return (False, pairs)
                            if 'default' in target_entry:
                                default = cast(t.TextEntry, target_entry)['default']
                                pairs[target] = default
                                return (False, pairs)
                            if value is not None:
                                pairs[target] = int(value)
                                return (True, pairs)

                            raise NullIntError(name, target)
                        case t.OptionType.COUNT:
                            old_value = cast(int, pairs.get(target, 0))
                            pairs[target] = old_value + 1
                        case t.OptionType.LIST:
                            if i < n - 1:
                                value = arg[i + 1:n]
                                sep = cast(t.ListEntry, target_entry).get('sep', ',')
                                pairs[target] = value.split(sep)
                                return (False, pairs)
                            elif value == '':
                                pairs[target] = []
                                return (True, pairs)
                            elif value is not None:
                                sep = cast(t.ListEntry, target_entry).get('sep', ',')
                                pairs[target] = value.split(sep)
                                return (True, pairs)

                            NullArgError(name, target)
                        case _:
                            msg = f'type {target_type} is not supported'
                            raise TypeError(msg)
                case _:
                    raise TypeError(f'type {tag} is not supported')

            i += 1

        return (False, pairs)
