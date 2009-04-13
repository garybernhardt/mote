import itertools

def describe_foo():
    calls = []
    def describe_nested():
        calls.append(1)
        assert calls == [1]
        def describe_nested_more():
            calls.append(2)
            assert calls == [1, 2]
            def describe_nested_even_more():
                calls.append(3)
                assert calls == [1, 2, 3]
                def should_have_fresh_iterator_the_first_time():
                    calls.append(4)
                    assert calls == [1, 2, 3, 4]
                def should_have_fresh_iterator_the_second_time():
                    calls.append(5)
                    assert calls == [1, 2, 3, 5]
        def describe_sibling_context_with_child():
            calls.append(6)
            assert calls == [1, 6]
            def describe_child_of_sibling():
                calls.append(7)
                assert calls == [1, 6, 7]
                def should_have_fresh_iterator():
                    calls.append(8)
                    assert calls == [1, 6, 7, 8]


# Output:
#
# foo nested nested more nested even more
#   - should have fresh iterator the first time
#   - should have fresh iterator the second time
# foo nested sibling context with child child of sibling
#   - should have fresh iterator
# All specs passed

