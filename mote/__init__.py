import unittest

from dingus import DingusTestCase


# XXX: Replace this!
#   1) It was not TDDed
#   2) It doesn't clean up after itself, leaving the module broken
def isolate(object_under_test, exclude=[]):
    def decorator(fn):
        def new_fn(*args, **kwargs):
            DingusTestCase(object_under_test, exclude=exclude)().setup()
            return fn(*args, **kwargs)
        new_fn.__name__ = fn.__name__
        return new_fn
    return decorator


def raises(exception, callable_, *args, **kwargs):
    try:
        assert_raises = DummyTestCase('nop').failUnlessRaises
        assert_raises(exception, callable_, *args, **kwargs)
    except AssertionError:
        return False
    else:
        return True


class DummyTestCase(unittest.TestCase):
    def nop(self):
        pass

