import os
import subprocess


def run_mote(test_file_name):
    base_dir = os.path.dirname(__file__)
    test_path = os.path.join(base_dir, test_file_name)
    process = subprocess.Popen(['python', '-m', 'mote', test_path],
                               stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.read()


def fails(spec_file_name):
    return run_mote(spec_file_name) == 'Specs failed\n'


def succeeds(spec_file_name):
    return run_mote(spec_file_name) == 'All specs passed\n'


def should_pass_with_no_tests():
    assert succeeds('spec_with_no_assertions.py')


def should_pass_with_one_test():
    assert succeeds('spec_with_one_assertion.py')


def should_fail_when_spec_raises_assertion_error():
    assert fails('spec_that_raises_assertion_error.py')

