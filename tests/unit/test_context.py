from dingus import Dingus, DingusFixture, exception_raiser
import mote
from mote import Context


class BaseFixture(DingusFixture(Context)):
    def setup(self):
        super(BaseFixture, self).setup()

    def _run_context_with_case_function(self, case_function):
        self.context_function = Dingus()
        mote.LocalFunctions.return_value = [self.case_function]
        mote.SortedFunctions.return_value = [self.case_function]
        self.context = Context(self.context_function)


class WhenRunningContextFromFunction(BaseFixture):
    def setup(self):
        super(WhenRunningContextFromFunction, self).setup()
        self.case_function = Dingus()
        self._run_context_with_case_function(self.case_function)

    def should_extract_spec_cases(self):
        assert mote.LocalFunctions.calls('()', self.context_function)

    def should_sort_functions(self):
        assert mote.SortedFunctions.calls('()', [self.case_function])

    def should_take_name_from_function(self):
        assert self.context.name is self.context_function.__name__


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

