def describe_something_that_fails():
    def it_will_fail_oh_noes():
        raise RuntimeError

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
# Specs failed

