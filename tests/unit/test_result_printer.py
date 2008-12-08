import sys

from dingus import Dingus, DingusFixture
import mote
from mote import ResultPrinter


class WithPatchedStdOut(DingusFixture(ResultPrinter)):
    def setup(self):
        super(WithPatchedStdOut, self).setup()
        mote.sys = Dingus()


class WhenGivenResults(WithPatchedStdOut):
    def setup(self):
        super(WhenGivenResults, self).setup()
        self.case = Dingus()
        self.context = Dingus(cases=[self.case])
        ResultPrinter([self.context])

    def should_print_context_name(self):
        assert mote.sys.stdout.calls('write', self.context.name + '\n').one()

    def should_print_case_name(self):
        assert mote.sys.stdout.calls('write', self.case.name + '\n').one()

