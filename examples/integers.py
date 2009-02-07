def describe_integers():
    def when_adding_one_and_one():
        x = 1 + 1
        def should_get_two():
            assert x == 2

    def when_dividing_by_zero():
        def should_raise_zero_division_error():
            assert_raises(ZeroDivisionError, lambda: 1 / 0)

# Output:
#
# describe integers
#   when adding one and one
#     should get two -> ok
#   when dividing by zero
#     should raise zero division error -> ok
# All specs passed

