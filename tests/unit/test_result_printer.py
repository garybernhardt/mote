import sys

from dingus import Dingus, DingusFixture
import mote
from mote import ResultPrinter


class WithPatchedStdOut(DingusFixture(ResultPrinter)):
    def setup(self):
        super(WithPatchedStdOut, self).setup()
        mote.sys = Dingus()


class WhenCasesPass(WithPatchedStdOut):
    def setup(self):
        super(WhenCasesPass, self).setup()
        self.case = Dingus(pretty_name='should frob')
        self.context = Dingus(pretty_name='describe frobber',
                              cases=[self.case])
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
                           exception=AssertionError())
        self.context = Dingus(pretty_name='describe frobber',
                              cases=[self.case])
        ResultPrinter([self.context])

    def should_print_failure_message(self):
        print mote.sys.stdout.calls
        assert mote.sys.stdout.calls(
            'write',
            '  should frob -> FAIL (AssertionError)\n').one()

