import os
import subprocess
import tempfile
from textwrap import dedent
import re


class SystemTest(object):
    def setup(self):
        self.test_file_path = tempfile.mktemp('mote_system_test')

    def _write_test_file(self, content):
        content = dedent(content)
        file(self.test_file_path, 'w').write(content)

    def _succeeds(self):
        return self._output('--quiet') == 'All specs passed\n'

    def _fails(self):
        return self._output('--quiet') == 'Specs failed\n'

    def _output(self, *args):
        return self._run_mote(self.test_file_path, *args)

    def _run_mote(self, test_file_name, *args):
        args = list(args)
        base_dir = os.path.dirname(__file__)
        test_path = os.path.join(base_dir, test_file_name)
        process = subprocess.Popen(['python', '-m', 'mote', test_path] + args,
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
        assert self._output('--quiet') == 'All specs passed\n'


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
        assert self._succeeds()

    def should_output_spec(self):
        expected = dedent(
            '''\
            describe_integers
            should_add_correctly
            All specs passed
            ''')
        assert self._output() == expected

class WhenRunningMote(SystemTest):
    def should_pass_with_no_tests(self):
        self._write_test_file('')
        assert self._succeeds()

    def should_fail_when_spec_raises_assertion_error(self):
        self._write_test_file('''
            def describe_integers_incorrectly():
                def should_add_incorrectly():
                    assert 1 + 1 == 3''')
        assert self._fails()

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


class WhenTestsHaveDifferentOrders(SystemTest):
    CONTEXT_DEF = 'def describe_ordered_tests():'
    FIRST_TEST_DEF = '    def first_test(): print "%s"'
    SECOND_TEST_DEF = '    def second_test(): print "%s"'

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

