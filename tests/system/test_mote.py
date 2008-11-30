import os
import subprocess


def run_mote(test_file_name):
    base_dir = os.path.dirname(__file__)
    test_path = os.path.join(base_dir, test_file_name)
    process = subprocess.Popen(['python', '-m', 'mote', test_path],
                               stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.read()


def should_pass_with_no_tests():
    assert run_mote('spec_with_no_assertions.py') == 'All specs passed\n'

def should_pass_with_one_test():
    assert run_mote('spec_with_one_assertion.py') == 'All specs passed\n'

def should_fail_when_spec_raises_assertion_error():
    assert run_mote('spec_that_raises_assertion_error.py') == 'Specs failed\n'

