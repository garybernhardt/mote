from dingus import Dingus, DingusTestCase, exception_raiser, DontCare
import mote
from mote import Case


class WhenRunningCase(DingusTestCase(Case)):
    def setup(self):
        super(WhenRunningCase, self).setup()
        self.context = Dingus()
        self.case_name = 'test_case_name'
        self.case = Case(self.context, self.case_name)

    def should_get_case_function_from_context(self):
        self.context.calls('fresh_function_named', self.case_name).one()

    def should_call_case_function(self):
        case_function = self.context.calls(
            'fresh_function_named').one().return_value
        assert case_function.calls('()').one()

    def should_have_name(self):
        assert self.case.name == 'test_case_name'

    def should_have_pretty_name(self):
        assert self.case.pretty_name == 'test case name'


class WhenTestFunctionRaisesNoException(DingusTestCase(Case)):
    def setup(self):
        super(WhenTestFunctionRaisesNoException, self).setup()
        self.context_function, self.case_name = Dingus.many(2)
        self.case = Case(self.context_function, self.case_name)

    def should_run_successfully(self):
        assert self.case.success


class WhenTestFunctionRaisesException(DingusTestCase(Case)):
    def setup(self):
        super(WhenTestFunctionRaisesException, self).setup()
        traceback = Dingus()
        traceback.tb_next.tb_lineno = 3
        mote.sys.exc_info.return_value = (Dingus(), Dingus(), traceback)

        self.context, self.case_name = Dingus.many(2)
        self.context.fresh_function_named.return_value = exception_raiser(
            AssertionError)
        self.case = Case(self.context, self.case_name)

    def should_fail(self):
        assert not self.case.success

    def should_store_exception(self):
        assert isinstance(self.case.exception, AssertionError)

    def should_store_line_number(self):
        assert self.case.exception_line == 3

