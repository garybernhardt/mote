def describe_integer():
    def describe_sum_of_one_and_one():
        x = 1 + 1
        def should_get_two():
            assert x == 2

    def describe_divided_by_zero():
        def should_raise_zero_division_error():
            assert raises(ZeroDivisionError, lambda: 1 / 0)

# Output:
#
# integer
#   sum of one and one
#     - should get two
#   divided by zero
#     - should raise zero division error
# All specs passed

