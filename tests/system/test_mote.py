import os
import subprocess
import tempfile


def run_mote(test_file_name):
    base_dir = os.path.dirname(__file__)
    test_path = os.path.join(base_dir, test_file_name)
    process = subprocess.Popen(['python', '-m', 'mote', test_path],
                               stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.read()


class WhenRunningMote:
    def setup(self):
        self.test_file_path = tempfile.mktemp('mote_system_test')

    def _write_test_file(self, content):
        file(self.test_file_path, 'w').write(content)

    def _succeeds(self):
        return run_mote(self.test_file_path) == 'All specs passed\n'

    def _fails(self):
        return run_mote(self.test_file_path) == 'Specs failed\n'

    def should_pass_with_no_tests(self):
        self._write_test_file('')
        assert self._succeeds()

    def should_pass_with_one_test(self):
        self._write_test_file('''
def describe_integers():
    def should_add_correctly():
        assert 1 + 1 == 2''')
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

