from mote import Context


def succeeds(context_fn):
    context = Context(context_fn)
    context.run()
    return context.success


def fails(context_fn):
    return not succeeds(context_fn)


def should_pass_with_no_tests():
    def describe_with_no_tests():
        pass
    assert succeeds(describe_with_no_tests)

def should_pass_with_one_test():
    def describe_with_one_test():
        def should_pass():
            pass
    assert succeeds(describe_with_one_test)

def should_fail_when_spec_raises_assertion_error():
    def describe_with_test_that_raises_assertion_error():
        def should_raise_error():
            assert 1 == 2
    assert fails(describe_with_test_that_raises_assertion_error)

def should_fail_when_spec_raises_value_error():
    def describe_with_test_that_raises_value_error():
        def should_raise_error():
            raise ValueError()
    assert fails(describe_with_test_that_raises_value_error)

