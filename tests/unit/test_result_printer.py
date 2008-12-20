import sys

from dingus import Dingus, DingusTestCase
import mote
from mote import ResultPrinter


class WithPatchedStdOut(DingusTestCase(ResultPrinter)):
    def setup(self):
        super(WithPatchedStdOut, self).setup()
        mote.sys = Dingus()


class WhenCasesPass(WithPatchedStdOut):
    def setup(self):
        super(WhenCasesPass, self).setup()
        self.case = Dingus(pretty_name='should frob')
        self.context = Dingus(pretty_name='describe frobber',
                              cases=[self.case],
                              contexts=[])
        ResultPrinter([self.context])

    def should_print_context_name(self):
        assert mote.sys.stdout.calls('write', 'describe frobber\n').one()

    def should_print_case_name(self):
        assert mote.sys.stdout.calls('write', '  should frob -> ok\n').one()


class WhenCasesFail(WithPatchedStdOut):
    def setup(self):
        super(WhenCasesFail, self).setup()
        self.case = Dingus(pretty_name='should frob',
                           success=False,
                           exception=AssertionError(),
                           exception_line=3)
        self.context = Dingus(pretty_name='describe frobber',
                              cases=[self.case],
                              contexts=[])
        ResultPrinter([self.context])

    def should_print_failure_message(self):
        print mote.sys.stdout.calls
        assert mote.sys.stdout.calls(
            'write',
            '  should frob -> FAIL (AssertionError @ 3)\n').one()


class WhenCasesAreInNestedContexts(WithPatchedStdOut):
    def setup(self):
        super(WhenCasesAreInNestedContexts, self).setup()
        self.case = Dingus(pretty_name='should frob',
                           success=True)
        self.inner_context = Dingus(pretty_name='when frobbing',
                                    cases=[self.case],
                                    contexts=[])
        self.outer_context = Dingus(pretty_name='describe frobber',
                                    contexts=[self.inner_context],
                                    cases=[])
        ResultPrinter([self.outer_context])

    def should_print_inner_context_results(self):
        assert mote.sys.stdout.calls('write', '  when frobbing\n')

