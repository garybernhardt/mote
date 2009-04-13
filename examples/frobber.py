# Class under test
class Frobber:
    def __init__(self):
        self.ready_to_frob = True
    def frazzle(self):
        self.ready_to_frob = False
    def frob(self):
        self.spam = 5


# Specs (tests)
def describe_frobber():
    frobber = Frobber()

    def should_be_ready_to_frob():
        assert frobber.ready_to_frob

    def should_not_have_spam():
        assert raises(AttributeError, lambda: frobber.spam)

    def describe_that_has_been_frazzled():
        frobber.frazzle()

        def should_not_be_ready_to_frob():
            assert not frobber.ready_to_frob

        def should_be_ready_to_frob(): # FAILS - contradicts previous test
            assert frobber.ready_to_frob

    def describe_that_has_been_frobbed():
        frobber.frob()

        def should_have_spam():
            assert frobber.spam


# Output:
#
# frobber
#   - should be ready to frob
#   - should not have spam
#   that has been frazzled
#     - should not be ready to frob
#     - should be ready to frob -> FAIL (AssertionError @ 28)
#
# Traceback (most recent call last):
#   File "$ROOT/examples/frobber.py", line 28, in should_be_ready_to_frob
#     assert frobber.ready_to_frob
# AssertionError
#
#   that has been frobbed
#     - should have spam
# Specs failed

