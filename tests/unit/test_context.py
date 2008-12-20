from dingus import Dingus, DingusTestCase, exception_raiser
import mote
from mote import Context


class BaseFixture(DingusTestCase(Context)):
    def setup(self):
        super(BaseFixture, self).setup()

        # Replace the Context class with a Dingus because it instantiates
        # child contexts
        mote.Context = Dingus()

    def _run_context_with_case_function(self, case_function):
        self.context_function = Dingus()
        self.context_function.__name__ = 'test_context_function'
        mote.LocalFunctions.case_functions.return_value = [self.case_function]
        mote.SortedFunctions.return_value = [self.case_function]
        self.context = Context(self.context_function)


class WhenRunningContextFromFunction(BaseFixture):
    def setup(self):
        super(WhenRunningContextFromFunction, self).setup()
        self.case_function = Dingus()
        self._run_context_with_case_function(self.case_function)

    def should_extract_spec_cases(self):
        assert mote.LocalFunctions.calls('case_functions',
                                         self.context_function)

    def should_sort_functions(self):
        assert mote.SortedFunctions.calls('()', [self.case_function])

    def should_take_name_from_function(self):
        assert self.context.name == 'test_context_function'

    def should_have_pretty_name(self):
        assert self.context.pretty_name == 'test context function'


class WhenRunningMultipleCases(BaseFixture):
    def setup(self):
        super(WhenRunningMultipleCases, self).setup()
        self.context_function = Dingus()
        self.case_functions = [Dingus(), Dingus()]
        mote.SortedFunctions.return_value = self.case_functions
        self.context = Context(self.context_function)

    def should_create_cases(self):
        assert all(mote.Case.calls('()',
                                   self.context_function,
                                   case_function.__name__).one()
                   for case_function in self.case_functions)

    def should_return_correct_number_of_cases(self):
        assert len(self.context.cases) == len(self.case_functions)


class WhenContextsAreNested(BaseFixture):
    def setup(self):
        super(WhenContextsAreNested, self).setup()

        def when_frobbing(): pass
        self.when_frobbing = when_frobbing
        def some_function(): pass

        mote.SortedFunctions.return_value = [when_frobbing]
        self.context_function = Dingus()
        self.context = Context(self.context_function)

    def should_create_context(self):
        assert mote.Context.calls('()').one()

    def should_collect_contexts(self):
        assert self.context.contexts == [mote.Context.return_value]

    def should_extract_context_functions(self):
        assert mote.LocalFunctions.calls('context_functions',
                                         self.context_function).one()

    def should_sort_extracted_context_functions(self):
        context_functions = mote.LocalFunctions.context_functions.return_value
        assert mote.SortedFunctions.calls('()', context_functions).one()

    def should_use_child_context_function_to_create_child_context(self):
        inner_context_function = mote.Context.calls('()').one().args[0]
        assert inner_context_function.__name__ == 'when_frobbing'

