def describe_a_list():
    def describe_containing_nothing():
        list_ = []

        def doesnt_contain_things():
            assert 5 not in list_

        def has_length_zero():
            assert len(list_) == 0

    def describe_containing_five_nones():
        list_ = [None] * 5

        def has_a_length():
            assert len(list_) == 5

        def knows_what_it_contains():
            assert None in list_

        def knows_what_it_doesnt_contain():
            assert 1 not in list_

# Output:
#
# a list containing nothing
#   - doesnt contain things
#   - has length zero
# a list containing five nones
#   - has a length
#   - knows what it contains
#   - knows what it doesnt contain
# OK

