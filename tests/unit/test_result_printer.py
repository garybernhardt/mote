import sys

from dingus import Dingus, DingusTestCase
import mote
from mote import ResultPrinter


class WithPatchedStdOut(DingusTestCase(ResultPrinter, 'count')):
    def setup(self):
        super(WithPatchedStdOut, self).setup()
        mote.sys = Dingus()

    def _wrote(self, text):
        return mote.sys.stdout.calls('write', text).one()


class WhenCasesPass(WithPatchedStdOut):
    def setup(self):
        super(WhenCasesPass, self).setup()
        self.case = Dingus(pretty_name='should frob')
        self.context = Dingus(pretty_name='frobber',
                              cases=[self.case],
                              contexts=[])
        ResultPrinter([self.context])

    def should_print_context_name(self):
        assert self._wrote('frobber\n')

    def should_print_case_name(self):
        assert self._wrote('  - should frob\n')


class WhenCasesFail(WithPatchedStdOut):
    def setup(self):
        super(WhenCasesFail, self).setup()
        self.case1 = Dingus(pretty_name='should 1',
                            success=False,
                            exception=AssertionError(),
                            failure=Dingus(exception_line=3))
        self.case2 = Dingus(pretty_name='should 2',
                            success=False,
                            exception=AssertionError(),
                            failure=Dingus(exception_line=5))
        self.context = Dingus(pretty_name='describe frobber',
                              cases=[self.case1, self.case2],
                              contexts=[])
        ResultPrinter([self.context])

    def should_print_failure_message(self):
        assert self._wrote('  - should 1 -> FAIL (AssertionError @ 3)\n')
        assert self._wrote('  - should 2 -> FAIL (AssertionError @ 5)\n')

    def should_number_failures(self):
        assert self.case1.failure.number == 1
        assert self.case2.failure.number == 2


class WhenCasesAreInNestedContexts(WithPatchedStdOut):
    def setup(self):
        super(WhenCasesAreInNestedContexts, self).setup()
        self.inner_context = Dingus(pretty_name='frobber that is awesome',
                                    cases=[Dingus(pretty_name='case')],
                                    contexts=[])
        self.outer_context = Dingus(contexts=[self.inner_context],
                                    cases=[])
        ResultPrinter([self.outer_context])

    def should_combine_context_names(self):
        assert self._wrote('frobber that is awesome\n')

    def shouldnt_print_anything_else(self):
        printed_lines = [call.args[0]
                         for call in mote.sys.stdout.calls('write')]
        assert set(printed_lines) == set(['frobber that is awesome\n',
                                          '  - case\n'])

