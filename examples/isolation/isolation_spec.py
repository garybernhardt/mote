from examples.isolation import module_under_test

@isolate(module_under_test.A)
def describe_isolation_on_class_A():
    def replaces_class_B_with_dingus():
        from dingus import Dingus
        assert isinstance(module_under_test.B, Dingus)

# Output:
#
# isolation on class A
#   - replaces class B with dingus
# OK

