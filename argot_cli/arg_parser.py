from abc import ABCMeta
import re
from typing import Final, TypedDict, cast

import argot_cli.argot_types as t
from argot_cli.argot_errors import (
    NullArgError,
    NullFloatError,
    NullIntError,
    UnknownOptionError,
)
from argot_cli.parser_config import ParserConfig
from argot_cli.argot_utils import parse_float, parse_int


class ArgParser:
    """
    Command-line argument parser.

    The parser processes an array of strings according to a
    configuration and produces a structured result.

    Parsing follows UNIX-style short options and GNU-style long
    options.
    """
    long_opt_exp = re.compile(r'^--')
    short_opt_exp = re.compile(r'^-[^-]')
    assignment_exp = re.compile(r'^--([^=]+)=(.+)?')
    parameter_exp = re.compile(r'^([^=]+)=(.+)?')
    _configs: ParserConfig
    __slots__ = ['_configs']

    def __init__(self, configs: ParserConfig, /):
        if not isinstance(configs, ParserConfig):
            raise TypeError('input value must be an instance of ParserConfig')
        self._configs = configs

    def parse(self, arg_list: list[str], /) -> t.ParseResult:
        """
        Parse an array of command-line arguments.

        Arguments are processed from left to right. Each argument is
        classified as one of:

        - option: matches a configured short or long option
        - parameter: of the form "key=value"
        - operand: any other argument

        Parsing rules:

        - The literal "--" stops option parsing. All subsequent
          arguments are treated as operands.
        - Short options may be combined (e.g. "-abc").
        - If a short option that accepts an associated value is not the
          last character in a group, the remainder of the argument is
          used as its value (e.g. "-n10").
        - If a short option that accepts an associated value appears as
          the last character:
            - If the option has a default value, no additional argument
              is consumed.
            - Otherwise, the next argument is used as its value.
        - Long options must be provided in the form "--name" if they do
          not accept an associated value, or "--name=value" if they do.
        - Long options that accept an associated value never consume
          the next argument.
        - Parameters are parsed from arguments matching "key=value" and
          are stored separately from options.
        - If an option is repeated:
            - count and list options accumulate values
            - other options overwrite previous values
        - Alias options store their values under the target option's
          name.

        Returns:
            A mapping with three entries:
            - options: parsed option values
            - parameters: key/value assignments
            - operands: positional arguments

        Raises:
            Error: if an unknown option is encountered or a required
            value is missing.
        """
        options = t.Options()
        parameters = t.Parameters()
        operands = t.Operands()

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
                    if self._configs[name]['type'] == 'count':
                        old_value = cast(int, options.get(name, 0))
                        new_value = cast(int, value)
                        options[name] = old_value + new_value
                    elif self._configs[name]['type'] == 'list':
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
        operands._freeze()
        return {
            'options': options,
            'parameters': parameters,
            'operands': operands,
        }

    def _parse_long_option(self, arg: str) -> tuple[str, t.OptionValue]:
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

        try:
            entry: t.ConfigEntry = self._configs[name]
        except KeyError:
            raise UnknownOptionError(name) from None

        tag: t.OptionType = entry['type']
        new_value: t.OptionValue
        default: str | int | float

        match tag:
            case 'flag':
                return (name, True)

            case 'text':
                if value is not None:
                    return (name, value)
                elif 'default' in entry:
                    default = cast(t.TextEntry, entry)['default']
                    return (name, default)

                raise NullArgError(name)

            case 'int':
                if value is not None and value != '':
                    return (name, parse_int(value))
                elif 'default' in entry:
                    default = cast(t.IntEntry, entry)['default']
                    return (name, default)

                raise NullIntError(name)

            case 'float':
                if value is not None and value != '':
                    return (name, parse_float(value))
                elif 'default' in entry:
                    default = cast(t.FloatEntry, entry)['default']
                    new_value = float(default)
                    return (name, new_value)

                raise NullFloatError(name)

            case 'count':
                if value is not None:
                    return (name, parse_int(value))
                return (name, 1)

            case 'list':
                if value == '':
                    return (name, [])
                elif value is not None:
                    sep = cast(t.ListEntry, entry).get('sep', ',')
                    return (name, value.split(sep))

                raise NullArgError(name)

            case 'alias':
                target = cast(t.AliasEntry, entry)['target']
                target_entry: t.ConfigEntry = self._configs[target]
                target_type: t.AliasType = cast(t.AliasType, target_entry['type'])

                match target_type:
                    case 'flag':
                        return (target, True)

                    case 'text':
                        if value is not None:
                            return (target, value)
                        elif 'default' in target_entry:
                            default = cast(t.TextEntry, target_entry)['default']
                            return (target, default)

                        raise NullArgError(name, target)

                    case 'int':
                        if value is not None and value != '':
                            return (target, parse_int(value))
                        elif 'default' in target_entry:
                            default = cast(t.IntEntry, target_entry)['default']
                            return (target, default)

                        raise NullIntError(name, target)

                    case 'float':
                        if value is not None and value != '':
                            return (target, parse_float(value))
                        elif 'default' in target_entry:
                            default = cast(t.FloatEntry, target_entry)['default']
                            new_value = float(default)
                            return (target, new_value)

                        raise NullFloatError(name, target)

                    case 'count':
                        if value is not None:
                            return (target, parse_int(value))
                        return (target, 1)

                    case 'list':
                        if value == '':
                            return (target, [])
                        elif value is not None:
                            sep = cast(t.ListEntry, target_entry).get('sep', ',')
                            return (target, value.split(sep))

                        raise NullArgError(name, target)

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
            try:
                entry = self._configs[name]
            except KeyError:
                raise UnknownOptionError(name) from None
            tag: str = entry['type']
            default: str | int | float

            match tag:
                case 'flag':
                    pairs[name] = True

                case 'text':
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

                case 'int':
                    if i < n - 1:
                        value = arg[i + 1:n]
                        pairs[name] = parse_int(value)
                        return (False, pairs)
                    elif 'default' in entry:
                        default = cast(t.IntEntry, entry)['default']
                        pairs[name] = default
                        return (False, pairs)
                    elif value is not None:
                        pairs[name] = parse_int(value)
                        return (True, pairs)

                    raise NullIntError(name)

                case 'float':
                    if i < n - 1:
                        value = arg[i + 1:n]
                        pairs[name] = parse_float(value)
                        return (False, pairs)
                    elif 'default' in entry:
                        default = cast(t.FloatEntry, entry)['default']
                        pairs[name] = float(default)
                        return (False, pairs)
                    elif value is not None:
                        pairs[name] = parse_float(value)
                        return (True, pairs)

                    raise NullFloatError(name)

                case 'count':
                    old_value = cast(int, pairs.get(name, 0))
                    pairs[name] = old_value + 1

                case 'list':
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

                case 'alias':
                    target: str = cast(t.AliasEntry, entry)['target']
                    target_entry: t.ConfigEntry = self._configs[target]
                    target_type: t.AliasType = cast(t.AliasType, target_entry['type'])

                    match target_type:
                        case 'flag':
                            pairs[target] = True

                        case 'text':
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

                        case 'int':
                            if i < n - 1:
                                value = arg[i + 1:n]
                                pairs[target] = parse_int(value)
                                return (False, pairs)
                            if 'default' in target_entry:
                                default = cast(t.IntEntry, target_entry)['default']
                                pairs[target] = default
                                return (False, pairs)
                            if value is not None:
                                pairs[target] = parse_int(value)
                                return (True, pairs)

                            raise NullIntError(name, target)

                        case 'float':
                            if i < n - 1:
                                value = arg[i + 1:n]
                                pairs[target] = parse_float(value)
                                return (False, pairs)
                            if 'default' in target_entry:
                                default = cast(t.FloatEntry, target_entry)['default']
                                pairs[target] = float(default)
                                return (False, pairs)
                            if value is not None:
                                pairs[target] = parse_float(value)
                                return (True, pairs)

                            raise NullFloatError(name, target)

                        case 'count':
                            old_value = cast(int, pairs.get(target, 0))
                            pairs[target] = old_value + 1

                        case 'list':
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

                            raise NullArgError(name, target)

            i += 1
        return (False, pairs)
