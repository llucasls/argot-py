from tests import TestCase

from argot_cli.argot_types import (
    Options,
    Parameters,
    Operands,
)


class TestOptions(TestCase):
    options = Options(jobs=4)

    def test_prevent_extra_properties_in_an_options_object(self):
        options = self.options.copy()

        with self.assertRaises(TypeError):
            options.output = 'build.log'

    def test_add_a_new_option(self):
        options = self.options.copy()

        options['list'] = True
        self.assertTrue('list' in options)

    def test_delete_option(self):
        options = self.options.copy()
        options['list'] = True

        del options['list']
        self.assertFalse('list' in options)

    def test_clear_options(self):
        options = self.options.copy()

        options.clear()
        self.assertEqual(len(options), 0)

    def test_freeze_options(self):
        options = self.options.copy()

        options._freeze()
        with self.assertRaises(TypeError):
            options['silent'] = True
        with self.assertRaises(TypeError):
            options.clear()
        with self.assertRaises(TypeError):
            options.pop('jobs')
        with self.assertRaises(TypeError):
            options.update(action='serve', mode='strict', host='example.com')

    def test_pop_parsed_option(self):
        options = self.options.copy()
        self.assertEqual(options.get('jobs'), 4)
        self.assertEqual(options.pop('jobs'), 4)
        self.assertIsNone(options.get('jobs'))

    def test_update(self):
        options = self.options.copy()

        options.update(action='serve', strict=True, host='example.com')
        self.assertDictEqual(
            options,
            {
                'jobs': 4,
                'action': 'serve',
                'strict': True,
                'host': 'example.com',
            }
        )


class TestParameters(TestCase):
    parameters = Parameters(name='John')

    def test_prevent_extra_properties_in_a_parameters_object(self):
        parameters = self.parameters.copy()

        with self.assertRaises(TypeError):
            parameters.name = 'John'

    def test_add_a_new_parameter(self):
        parameters = self.parameters.copy()

        parameters['job'] = 'carpenter'
        self.assertTrue('job' in parameters)

    def test_delete_parameter(self):
        parameters = self.parameters.copy()

        self.assertEqual(parameters.get('name'), 'John')
        del parameters['name']
        self.assertFalse('name' in parameters)

    def test_freeze_parameters(self):
        parameters = self.parameters.copy()
        parameters['job'] = 'carpenter'
        parameters._freeze()

        with self.assertRaises(TypeError):
            parameters['schooling'] = 'high school'
        with self.assertRaises(TypeError):
            del parameters['job']
        with self.assertRaises(TypeError):
            parameters.popitem()
        with self.assertRaises(TypeError):
            parameters.setdefault('action', 'exec')

    def test_pop_item(self):
        parameters = self.parameters.copy()

        self.assertEqual(parameters.get('name'), 'John')
        self.assertTupleEqual(parameters.popitem(), ('name', 'John'))
        self.assertIsNone(parameters.get('name'))

    def test_setdefault(self):
        parameters = self.parameters.copy()

        parameters.setdefault('action', 'exec')
        self.assertEqual(parameters['action'], 'exec')
        parameters['action'] = 'spawn'
        self.assertEqual(parameters['action'], 'spawn')


class TestOperands(TestCase):
    operands = Operands(['output.log', 'error.log'])

    def test_prevent_extra_properties_in_an_operands_object(self):
        operands = self.operands.copy()

        with self.assertRaises(TypeError):
            operands.file = 'build.log'

    def test_add_a_new_operand(self):
        operands = self.operands.copy()

        operands.append('extra.log')

    def test_freeze_operands(self):
        operands = self.operands.copy()
        operands._freeze()

        with self.assertRaises(TypeError):
            operands[0] = 'access.log'
        with self.assertRaises(TypeError):
            del operands[1]
        with self.assertRaises(TypeError):
            operands.append('linter.log')
        with self.assertRaises(TypeError):
            operands.reverse()
        with self.assertRaises(TypeError):
            operands.sort()
        with self.assertRaises(TypeError):
            operands.insert(1, 'check.log')
        with self.assertRaises(TypeError):
            operands.pop()
        with self.assertRaises(TypeError):
            operands.extend(['check.log', 'access.log'])
        with self.assertRaises(TypeError):
            operands.remove('error.log')
        with self.assertRaises(TypeError):
            operands.clear()

    def test_spawn_empty_operands_list(self):
        operands = Operands()
        self.assertListEqual(operands, [])

    def test_reverse_operands_list(self):
        operands = self.operands.copy()
        operands.reverse()
        self.assertListEqual(operands, ['error.log', 'output.log'])

    def test_sort_operands_list(self):
        operands = self.operands.copy()
        operands.sort()
        self.assertListEqual(operands, ['error.log', 'output.log'])

    def test_change_operand(self):
        operands = self.operands.copy()
        operands[0] = 'access.log'
        self.assertListEqual(operands, ['access.log', 'error.log'])

    def test_delete_operand(self):
        operands = self.operands.copy()
        del operands[0]
        self.assertListEqual(operands, ['error.log'])

    def test_clear_operands(self):
        operands = self.operands.copy()
        operands.clear()
        self.assertListEqual(operands, [])

    def test_extend_operands(self):
        operands = self.operands.copy()
        operands.extend(['check.log', 'access.log'])
        self.assertListEqual(operands, [
            'output.log',
            'error.log',
            'check.log',
            'access.log',
        ])

    def test_insert_operand(self):
        operands = self.operands.copy()
        operands.insert(1, 'access.log')
        self.assertListEqual(operands, ['output.log', 'access.log', 'error.log'])

    def test_pop_operand(self):
        operands = self.operands.copy()
        operands.pop()
        self.assertListEqual(operands, ['output.log'])

    def test_remove_operand(self):
        operands = self.operands.copy()
        operands.remove('output.log')
        self.assertListEqual(operands, ['error.log'])
