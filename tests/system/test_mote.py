import os
import subprocess
import tempfile
from textwrap import dedent
import re


class SystemTest(object):
    def setup(self):
        self.test_file_path = tempfile.mktemp('mote_system_test.py')

    def _write_test_file(self, content):
        content = dedent(content)
        file(self.test_file_path, 'w').write(content)

    def _output(self, test_paths=None, args=None):
        if test_paths is None:
            test_paths = [self.test_file_path]
        return self._run_mote(test_paths, args)

    def _assert_output_equals(self,
                              expected_output,
                              test_paths=None,
                              args=None):
        output = self._output(test_paths, args)
        if output != dedent(expected_output):
            raise AssertionError(
                'Expected output:\n---\n%s\n---\nbut got:\n---\n%s\n---\n' %
                (expected_output, output))

    def _assert_output_contains(self, expected_output, args=None):
        assert dedent(expected_output) in self._output(args=args)

    def _assert_succeeds(self):
        self._assert_output_equals('OK\n', args=['--quiet'])

    def _assert_fails(self):
        self._assert_output_equals('Specs failed\n', args=['--quiet'])

    def _run_mote(self, test_paths, args):
        args = [] if args is None else args
        process = subprocess.Popen(
            ['python', '-m', 'mote.runner'] + test_paths + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        process.wait()
        return process.stdout.read()


class WhenRunningQuietly(SystemTest):
    def should_only_output_result(self):
        self._write_test_file(
            '''
            def describe_integers():
                def should_add_correctly():
                    assert 1 + 1 == 2
            ''')
        self._assert_output_equals('OK\n', args=['--quiet'])


class WhenCasesRaiseNoExceptions(SystemTest):
    def setup(self):
        super(WhenCasesRaiseNoExceptions, self).setup()
        self._write_test_file(
            '''
            def describe_integers():
                def should_add_correctly():
                    assert 1 + 1 == 2
            ''')

    def should_pass(self):
        self._assert_succeeds()

    def should_output_spec(self):
        expected = dedent(
            '''\
            integers
              - should add correctly
            OK
            ''')
        self._assert_output_equals(expected)


class WhenCasesRaiseExceptions(SystemTest):
    def setup(self):
        super(WhenCasesRaiseExceptions, self).setup()
        self._write_test_file('''\
            def describe_integers_incorrectly():
                def should_add_correctly():
                    assert 1 + 1 == 2
                def should_add_incorrectly():
                    assert 1 + 1 == 3''')

    def should_fail(self):
        self._assert_fails()

    def should_output_spec_with_failures(self):
        output = self._output()
        assert 'should add incorrectly -> FAIL (AssertionError @ 5)' in output


class WhenRunningMote(SystemTest):
    def should_pass_with_no_tests(self):
        self._write_test_file('')
        self._assert_succeeds()

    def should_fail_when_spec_raises_unknown_error(self):
        self._write_test_file('''
            class FooException(Exception):
                pass
            def describe_with_test_that_raises_value_error():
                def should_raise_error():
                    raise ValueError()''')

    def should_rerun_context_for_each_test(self):
        self._write_test_file(
            '''
            import itertools
            iterator = itertools.count()
            def describe_test_with_stateful_context():
                value = iterator.next()
                def should_use_object():
                    print value
                def should_use_different_object_on_second_run():
                    print value
            ''')
        output = self._output()
        printed_values = re.search(r'^(\d+)\n(\d+)\n', output).groups()
        assert printed_values[1] > printed_values[0]

    def should_only_include_contexts_starting_with_describe(self):
        self._write_test_file(
            '''
            def some_callable():
                pass
            def describe_foo():
                def should_do_stuff():
                    pass
            ''')
        self._assert_output_equals(
            '''\
            foo
              - should do stuff
            OK
            ''')

    def should_treat_callables_as_specs(self):
        self._write_test_file(
            '''
            def describe_integers():
                def can_be_added():
                    assert 1 + 1 == 2
            ''')
        self._assert_output_equals(
            '''\
            integers
              - can be added
            OK
            ''')

    def should_not_treat_functions_with_leading_underscores_as_specs(self):
        self._write_test_file(
            '''
            def describe_integers():
                def should_do_stuff():
                    pass
                def _not_a_spec():
                    pass
            ''')
        self._assert_output_equals(
            '''\
            integers
              - should do stuff
            OK
            ''')

    def should_not_treat_callables_that_arent_functions_as_specs(self):
        self._write_test_file(
            '''
            class Callable:
                def __call__(self):
                    pass
            def describe_integers():
                def should_do_stuff():
                    pass
                callable = Callable()
            ''')
        self._assert_output_equals(
            '''\
            integers
              - should do stuff
            OK
            ''')


class WhenContextsAreNested(SystemTest):
    def setup(self):
        super(WhenContextsAreNested, self).setup()
        self._write_test_file(
            '''
            def describe_integers():
                def should_be_built_in():
                    assert 'int' in __builtins__
                def describe_adding():
                    value = 1 + 1
                    def should_get_sum():
                        assert value == 2
                    def describe_something_is_wrong():
                        def should_fail():
                            assert 1 == 2
            ''')

    def should_run_cases_in_nested_contexts(self):
        assert 'should get sum' in self._output()

    def should_run_cases_before_contexts_within_same_parent_context(self):
        output = self._output()
        case_location = output.index('should be built in')
        context_location = output.index('adding')
        assert case_location < context_location

    def should_report_failing_specs(self):
        self._assert_fails()


class WhenRunningStatefulNestedContexts(SystemTest):
    def should_rerun_outer_context_for_each_test(self):
        self._write_test_file('''
            import itertools
            def describe_test_with_stateful_context():
                iterator = itertools.count()
                def describe_in_inner_context():
                    def should_get_0_from_iterator_in_first_case():
                        assert iterator.next() == 0
                    def should_get_1_from_iterator_in_second_case():
                        assert iterator.next() == 0
            ''')
        self._assert_succeeds()

    def should_rerun_grandparent_context_for_each_context(self):
        self._write_test_file('''
            def describe_test_with_stateful_context():
                calls = ['describe']
                def describe_1():
                    calls.append('describe_1')
                    assert calls == ['describe', 'describe_1']
                    def should_1():
                        calls.append('should_1')
                        assert calls == ['describe', 'describe_1', 'should_1']
                def describe_2():
                    calls.append('describe_2')
                    assert calls == ['describe', 'describe_2']
                    def should_2():
                        calls.append('should_2')
                        assert calls == ['describe', 'describe_2', 'should_2']
            ''')
        self._assert_succeeds()


class WhenTestsHaveDifferentOrders(SystemTest):
    CONTEXT_DEF = 'def describe_ordered_tests():'
    FIRST_TEST_DEF = '    def should_do_first_test(): print "%s"'
    SECOND_TEST_DEF = '    def should_do_second_test(): print "%s"'

    def should_run_tests_in_order(self):
        self._write_test_file('\n'.join([self.CONTEXT_DEF,
                                         self.FIRST_TEST_DEF % '1',
                                         self.SECOND_TEST_DEF % '2']))
        assert self._output()[:3] == '1\n2'

    def should_run_tests_in_order_when_reversed(self):
        self._write_test_file('\n'.join([self.CONTEXT_DEF,
                                         self.SECOND_TEST_DEF % '1',
                                         self.FIRST_TEST_DEF % '2']))
        assert self._output()[:3] == '1\n2'


class WhenTestsAreInNestedDirectories(SystemTest):
    def _assert_finds_file_at_path(self, parent_path, test_path):
        file(test_path, 'w').write(dedent(
            '''
            def describe_nested_file():
                def should_do_stuff():
                    pass
            '''))
        self._assert_output_equals(
            '''\
            nested file
              - should do stuff
            OK
            ''',
            test_paths=[parent_path])

    def should_find_tests_nested_one_level_deep(self):
        dir_path = tempfile.mkdtemp('mote_system_test')
        file_path = os.path.join(dir_path, 'test_file.py')
        self._assert_finds_file_at_path(dir_path, file_path)

    def should_find_tests_nested_two_levels_deep(self):
        dir_path = tempfile.mkdtemp('mote_system_test')
        subdir = os.path.join(dir_path, 'subdir')
        os.mkdir(subdir)
        file_path = os.path.join(subdir, 'test_file.py')
        self._assert_finds_file_at_path(dir_path, file_path)


class WhenMultipleTestFilesExist(SystemTest):
    def setup(self):
        self.dir_path = tempfile.mkdtemp('mote_system_test')
        first_test_path = os.path.join(self.dir_path, 'first_test.py')
        second_test_path = os.path.join(self.dir_path, 'second_test.py')
        for path in [first_test_path, second_test_path]:
            file(path, 'w').write(dedent(
                '''
                def describe_path():
                    def should_do_stuff():
                        pass
                '''))

    def should_find_both_files(self):
        self._assert_output_equals(
            '''\
            path
              - should do stuff
            path
              - should do stuff
            OK
            ''',
            test_paths=[self.dir_path])


class WhenMultipleTestFilesAreGivenAsArguments(SystemTest):
    def setup(self):
        super(WhenMultipleTestFilesAreGivenAsArguments, self).setup()
        root = os.path.join(os.path.dirname(__file__),
                            'fixtures',
                            'multiple_files')
        self.paths = [os.path.join(root, 'spec_file_%i.py' % index)
                      for index in (1, 2)]

    def should_run_all_files(self):
        self._assert_output_equals(
            '''\
            spec file 1
              - should be run
            spec file 2
              - should be run
            OK
            ''',
            test_paths=self.paths)


class WhenASpecFileFailsToImport(SystemTest):
    def setup(self):
        super(WhenASpecFileFailsToImport, self).setup()
        self._write_test_file('raise Exception')

    def should_print_traceback(self):
        self._assert_output_contains(
            'line 1, in <module>\n    raise Exception')

    def should_print_traceback_when_running_quietly(self):
        self._assert_output_contains(
            'line 1, in <module>\n    raise Exception',
            args=['-q'])

