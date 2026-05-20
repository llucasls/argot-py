from tests import TestCase

from argot_cli.parser_config import ParserConfig
from argot_cli.arg_parser import ArgParser
from argot_cli.argot_errors import (
    NullArgError,
    NullFloatError,
    NullIntError,
    UnknownOptionError,
)
from argot_cli.argot_types import (
    ConfigEntries,
    Options,
    Parameters,
    Operands,
)


class TestArgParser(TestCase):
    options: ConfigEntries = {
        'strict': { 'type': 'flag' },
        'output': { 'type': 'text' },
        'output-file': { 'type': 'alias', 'target': 'output' },
        'logfile': { 'type': 'text', 'default': 'access.log' },
        'log-file': { 'type': 'alias', 'target': 'logfile' },
        'retries': { 'type': 'int' },
        'retry': { 'type': 'alias', 'target': 'retries' },
        'threads': { 'type': 'int', 'default': 0 },
        'jobs': { 'type': 'alias', 'target': 'threads' },
        'loglevel': { 'type': 'count' },
        'verbosity': { 'type': 'alias', 'target': 'loglevel' },
        'tasks': { 'type': 'list' },
        'path': { 'type': 'alias', 'target': 'P' },
        'dry-run': { 'type': 'alias', 'target': 'n' },
        'user': { 'type': 'alias', 'target': 'u' },
        'id': { 'type': 'alias', 'target': 'i' },
        'targets': { 'type': 'alias', 'target': 't' },
        'permission': { 'type': 'alias', 'target': 'p' },
        'n': { 'type': 'flag' },
        'u': { 'type': 'text' },
        'U': { 'type': 'alias', 'target': 'u' },
        'g': { 'type': 'text' },
        'G': { 'type': 'alias', 'target': 'g' },
        'e': { 'type': 'text', 'default': 'test' },
        'i': { 'type': 'int' },
        'I': { 'type': 'alias', 'target': 'i' },
        'j': { 'type': 'int' },
        'J': { 'type': 'alias', 'target': 'threads' },
        'a': { 'type': 'int', 'default': 0 },
        't': { 'type': 'list' },
        'p': { 'type': 'count' },
        'v': { 'type': 'alias', 'target': 'loglevel' },
        's': { 'type': 'alias', 'target': 'strict' },
        'o': { 'type': 'alias', 'target': 'output' },
        'O': { 'type': 'alias', 'target': 'logfile' },
        'r': { 'type': 'alias', 'target': 'retries' },
        'f': { 'type': 'alias', 'target': 'logfile' },
        'P': { 'type': 'list', 'sep': ':' },
        'T': { 'type': 'alias', 'target': 'tasks' },
        'E': { 'type': 'list' },
    }

    parser_config = ParserConfig({'options': options})

    parser = ArgParser(parser_config)

    def test_create_arg_parser_object(self):
        parser = ArgParser(self.parser_config)
        self.assertIsInstance(parser, ArgParser)

    def test_raise_error_on_invalid_parser_config(self):
        with self.assertRaises(TypeError):
            ArgParser(self.options)

    def test_raise_error_on_invalid_input_type(self):
        with self.assertRaises(TypeError):
            self.parser.parse('spec.txt')
        with self.assertRaises(TypeError):
            self.parser.parse([1, 2])

    def test_produce_result_with_specialized_types(self):
        result = self.parser.parse(['--strict', 'CC=clang', 'main.o'])

        self.assertIsInstance(result['options'], Options)
        self.assertIsInstance(result['parameters'], Parameters)
        self.assertIsInstance(result['operands'], Operands)

    def test_parse_parameters(self):
        result = self.parser.parse(['CC=clang', 'ENV=', '=', '=test'])

        expected_parameters = {
            'CC': 'clang',
            'ENV': '',
        }
        expected_operands = [
            '=',
            '=test',
        ]

        self.assertDictEqual(result['parameters'], expected_parameters)
        self.assertListEqual(result['operands'], expected_operands)

    def test_parse_parameters_as_normal_operands(self) -> None:
        parser = ArgParser(ParserConfig({
            'options': self.options,
            'parser': {
                'parseParameters': False
            }
        }))
        result = parser.parse(['CC=clang', 'ENV=', '=', '=test'])

        self.assertListEqual(
            result['operands'],
            ['CC=clang', 'ENV=', '=', '=test']
        )

    def test_parse_flag_options(self):
        result = self.parser.parse(['--strict', 'CC=clang', 'main.o', '-n'])

        expected_options = {
            'strict': True,
            'n': True,
        }
        expected_operands = ['main.o']

        self.assertDictEqual(result['options'], expected_options)
        self.assertListEqual(result['operands'], expected_operands)

    def test_parse_text_options(self):
        result = self.parser.parse([
            '--output=doc.txt',
            '--logfile',
            '-ubob',
            '-g',
            'users',
            '-e',
        ])

        expected = {
            'output': 'doc.txt',
            'logfile': 'access.log',
            'u': 'bob',
            'g': 'users',
            'e': 'test',
        }

        self.assertDictEqual(result['options'], expected)

    def test_parse_int_options(self):
        result = self.parser.parse([
            '--retries=3',
            '--threads',
            '-j4',
            '-i',
            '2',
            '-a',
        ])

        expected = {
            'retries': 3,
            'threads': 0,
            'i': 2,
            'j': 4,
            'a': 0,
        }

        self.assertDictEqual(result['options'], expected)

    def test_parse_float_options(self):
        parser = ArgParser(ParserConfig({
            'options': {
                'opacity': {'type': 'float'},
                'O': {'type': 'alias', 'target': 'opacity'},
                'z': {'type': 'float'},
                'zoom': {'type': 'alias', 'target': 'z'},
                'scale': {'type': 'float', 'default': 1.0},
                'S': {'type': 'float', 'default': 1.0},
                's': {'type': 'alias', 'target': 'S'},
                'bg-scale': {'type': 'alias', 'target': 'scale'},
                'bg-opacity': {'type': 'alias', 'target': 'opacity'},
            }
        }))

        result = parser.parse(['-O', '0.95', '-S1.25', '--zoom=1.5'])
        expected = {
            'opacity': 0.95,
            'S': 1.25,
            'z': 1.5,
        }
        self.assertDictEqual(result['options'], expected)

        result = parser.parse(['--opacity=0.8', '-z1', '--scale=2'])
        expected = {
            'opacity': 0.8,
            'z': 1.0,
            'scale': 2.0,
        }
        self.assertDictEqual(result['options'], expected)

        result = parser.parse(['--scale', '-S'])
        expected = {
            'scale': 1.0,
            'S': 1.0,
        }
        self.assertDictEqual(result['options'], expected)

        result = parser.parse(['--bg-scale', '-s'])
        expected = {
            'scale': 1.0,
            'S': 1.0,
        }
        self.assertDictEqual(result['options'], expected)

        result = parser.parse(['-z', '2', '-O.95'])
        expected = {
            'z': 2.0,
            'opacity': 0.95,
        }
        self.assertDictEqual(result['options'], expected)

        with self.assertRaises(NullFloatError):
            parser.parse(['--opacity'])

        with self.assertRaises(NullFloatError):
            parser.parse(['-z'])

        with self.assertRaises(NullFloatError):
            parser.parse(['-O'])

        with self.assertRaises(NullFloatError):
            parser.parse(['--bg-opacity'])

    def test_parse_count_options(self):
        result = self.parser.parse(['--loglevel=2', '-pp', '-p'])

        expected = {
            'loglevel': 2,
            'p': 3,
        }

        self.assertDictEqual(result['options'], expected)

    def test_parse_list_options(self):
        result = self.parser.parse([
            '--tasks=build,test',
            '--path=~/.local/bin:~/bin',
            '-P',
            '~/.cargo/bin',
            '-T',
            'all',
            '-Etest,staging',
            '-E',
            'build',
        ])

        expected = {
            'tasks': ['build', 'test', 'all'],
            'P': ['~/.local/bin', '~/bin', '~/.cargo/bin'],
            'E': ['test', 'staging', 'build'],
        }

        self.assertDictEqual(result['options'], expected)

    def test_parse_alias_options(self):
        result = self.parser.parse([
            '-vvv',
            '-so',
            'doc.txt',
            '-Ujohn',
            '-G',
            'staff',
            '-O',
            '-J',
            '-r4',
            '-I',
            '12',
            '-Tbuild',
            '-T',
            'check',
            '-T',
            '',
        ])

        expected = {
            'loglevel': 3,
            'logfile': 'access.log',
            'strict': True,
            'output': 'doc.txt',
            'threads': 0,
            'retries': 4,
            'tasks': ['build', 'check'],
            'u': 'john',
            'g': 'staff',
            'i': 12,
        }

        self.assertDictMatch(result['options'], expected)

    def test_parse_options_as_operands(self):
        result = self.parser.parse(['-vvv', '--', '-so', '--', 'doc.txt'])

        self.assertDictEqual(result['options'], {'loglevel': 3})
        self.assertListEqual(result['operands'], ['-so', '--', 'doc.txt'])

    def test_parse_list_option_with_empty_values(self):
        result = self.parser.parse(['--tasks=', '-P', ''])
        expected = {'tasks': [], 'P': []}

        self.assertDictEqual(result['options'], expected)

    def test_count_option_without_value(self):
        result = self.parser.parse(['--loglevel'])
        expected = {'loglevel': 1}

        self.assertDictEqual(result['options'], expected)

    def test_raise_error_on_text_option_without_associated_value(self):
        with self.assertRaises(NullArgError):
            self.parser.parse(['--output'])

        with self.assertRaises(NullArgError):
            self.parser.parse(['-u'])

        # alias to output
        with self.assertRaises(NullArgError):
            self.parser.parse(['--output-file'])

        # alias to output
        with self.assertRaises(NullArgError):
            self.parser.parse(['-o'])

    def test_raise_error_on_int_option_without_associated_value(self):
        with self.assertRaises(NullIntError):
            self.parser.parse(['--retries'])

        with self.assertRaises(NullIntError):
            self.parser.parse(['-j'])

        # alias to retries
        with self.assertRaises(NullIntError):
            self.parser.parse(['--retry'])

        # alias to retries
        with self.assertRaises(NullIntError):
            self.parser.parse(['-r'])

    def test_raise_error_on_list_option_without_associated_value(self):
        with self.assertRaises(NullArgError):
            self.parser.parse(['--tasks'])

        with self.assertRaises(NullArgError):
            self.parser.parse(['-P'])

        # alias to P
        with self.assertRaises(NullArgError):
            self.parser.parse(['--path'])

        # alias to tasks
        with self.assertRaises(NullArgError):
            self.parser.parse(['-T'])

    def test_parse_alias_long_options(self):
        result = self.parser.parse([
            '--dry-run',
            '--user=bob',
            '--id=7525',
            '--targets=build,ci,test',
            '--permission=3',
            '--jobs',
            '--log-file',
            '--verbosity',
            '--path=',
        ])

        expected = {
            'i': 7525,
            'logfile': 'access.log',
            'loglevel': 1,
            'n': True,
            'p': 3,
            't': ['build', 'ci', 'test'],
            'threads': 0,
            'u': 'bob',
            'P': [],
        }

        self.assertDictEqual(result['options'], expected)

    def test_raise_error_on_unsupported_options(self):
        with self.assertRaises(UnknownOptionError):
            self.parser.parse(['esto', '--no-ecxiste'])
        with self.assertRaises(UnknownOptionError):
            self.parser.parse(['-Z'])
