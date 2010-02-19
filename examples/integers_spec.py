from __future__ import with_statement
from expecter import expect

def describe_integer():
    def describe_when_adding_one_and_one():
        x = 1 + 1
        def should_get_two():
            assert x == 2

    def raises_error_when_dividing_by_zero():
        with expect.raises(ZeroDivisionError):
            1 / 0

# Output:
#
# integer
# integer when adding one and one
#   - should get two
#   - raises error when dividing by zero
# OK

