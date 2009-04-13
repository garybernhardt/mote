import itertools

def describe_foo():
    iterator = itertools.count()
    def describe_nested():
        def describe_nested_more():
            def describe_nested_even_more():
                def should_have_a_fresh_iterator_the_first_time():
                    assert iterator.next() == 0
                def should_have_a_fresh_iterator_the_second_time():
                    assert iterator.next() == 0


# Output:
#
# describe foo
#   describe nested
#     describe nested more
#       describe nested even more
#         - should have a fresh iterator the first time
#         - should have a fresh iterator the second time
# All specs passed

