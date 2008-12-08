from dingus import Dingus, DingusFixture, exception_raiser, DontCare
import mote
from mote import Case


class WhenRunningCase(DingusFixture(Case)):
    def setup(self):
        super(WhenRunningCase, self).setup()
        self.context_function = Dingus()
        self.case_name = 'test_case_name'
        self.case = Case(self.context_function, self.case_name)

    def should_get_local_functions_from_context_to_ensure_isolation(self):
        assert mote.LocalFunctions.calls('()',
                                         self.context_function,
                                         self.case_name).one()

    def should_run_cases_with_fresh_context(self):
        local_functions = mote.LocalFunctions.return_value
        case_function = local_functions.calls(
            'function_with_name', self.case_name).one().return_value
        assert case_function.calls('()').one()

    def should_have_name(self):
        assert self.case.name == 'test_case_name'

    def should_have_pretty_name(self):
        assert self.case.pretty_name == 'test case name'


class WhenTestFunctionRaisesNoException(DingusFixture(Case)):
    def setup(self):
        super(WhenTestFunctionRaisesNoException, self).setup()
        self.context_function, self.case_name = Dingus.many(2)
        self.case = Case(self.context_function, self.case_name)

    def should_run_successfully(self):
        assert self.case.success


class WhenTestFunctionRaisesException(DingusFixture(Case)):
    def setup(self):
        super(WhenTestFunctionRaisesException, self).setup()
        local_functions = mote.LocalFunctions.return_value
        local_functions.function_with_name.return_value = exception_raiser(
            AssertionError)

        traceback = Dingus()
        traceback.tb_next.tb_lineno = 3
        mote.sys.exc_info.return_value = (Dingus(), Dingus(), traceback)

        self.context_function, self.case_name = Dingus.many(2)
        self.case = Case(self.context_function, self.case_name)

    def should_fail(self):
        assert not self.case.success

    def should_store_exception(self):
        assert isinstance(self.case.exception, AssertionError)

    def should_store_line_number(self):
        assert self.case.exception_line == 3

