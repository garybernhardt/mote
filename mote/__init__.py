from dingus import DingusTestCase


# XXX: Remove this!
#   1) It was not TDDed
#   2) It doesn't clean up after itself, leaving the module broken
#   3) It belongs in Dingus, not Mote
def isolate(object_under_test, exclude=[]):
    def decorator(fn):
        def new_fn(*args, **kwargs):
            DingusTestCase(object_under_test, exclude=exclude)().setup()
            return fn(*args, **kwargs)
        new_fn.__name__ = fn.__name__
        return new_fn
    return decorator

