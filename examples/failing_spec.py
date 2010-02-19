def describe_something_that_fails():
    def it_will_fail_oh_noes():
        raise RuntimeError

def describe_an_error_in_a_context():
    raise RuntimeError
    def it_never_evaluates_its_cases():
        pass

def describe_failures_in_helpers():
    def _failing_helper():
        raise RuntimeError
    def fails_in_the_helper():
        _failing_helper()

# Output:
#
# something that fails
#   - it will fail oh noes -> FAIL (RuntimeError @ 3)
# 
# Traceback (most recent call last):
#   File "$ROOT/examples/failing_spec.py", line 3, in it_will_fail_oh_noes
#     raise RuntimeError
# RuntimeError
#
#   - an error in a context -> FAIL (RuntimeError @ 6)
#
# Traceback (most recent call last):
#   File "$ROOT/examples/failing_spec.py", line 6, in describe_an_error_in_a_context
#     raise RuntimeError
# RuntimeError
#
# failures in helpers
#   - fails in the helper -> FAIL (RuntimeError @ 14)
# 
# Traceback (most recent call last):
#   File "$ROOT/examples/failing_spec.py", line 14, in fails_in_the_helper
#     _failing_helper()
#   File "$ROOT/examples/failing_spec.py", line 12, in _failing_helper
#     raise RuntimeError
# RuntimeError
# 
# Specs failed

