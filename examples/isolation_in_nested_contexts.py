import itertools

def describe_foo():
    iterator = itertools.count()
    def when_nested():
        def when_nested_more():
            def when_nested_even_more():
                def should_have_a_fresh_iterator_the_first_time():
                    assert iterator.next() == 0
                def should_have_a_fresh_iterator_the_second_time():
                    assert iterator.next() == 0


# Output:
#
# describe foo
#   when nested
#     when nested more
#       when nested even more
#         should have a fresh iterator the first time -> ok
#         should have a fresh iterator the second time -> ok
# All specs passed

