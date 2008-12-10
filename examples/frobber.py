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
        assert_raises(AttributeError, lambda: frobber.spam)

    def when_frazzled():
        frobber.frazzle()

        def should_not_be_ready_to_frob():
            assert not frobber.ready_to_frob

        def should_be_ready_to_frob(): # FAILS - contradicts previous test
            assert frobber.ready_to_frob

    def when_frobbed():
        frobber.frob()

        def should_have_spam():
            assert frobber.spam


# Output:
#
# describe frobber
#   should be ready to frob -> ok
#   should not have spam -> ok
#   when frazzled
#     should not be ready to frob -> ok
#     should be ready to frob -> FAIL (AssertionError @ 28)
#   when frobbed
#     should have spam -> ok
# All specs passed

