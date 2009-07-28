import sys

from dingus import Dingus, DingusTestCase
import mote
from mote import QuietPrinter
from tests.unit.patchedstdout import PatchedStdoutMixin


class BaseFixture(DingusTestCase(QuietPrinter),
                  PatchedStdoutMixin(mote)):
    pass

class WhenCasesPass(BaseFixture):
    def setup(self):
        super(WhenCasesPass, self).setup()
        suite = Dingus(success=True)
        QuietPrinter(suite).print_result()

    def should_print_ok(self):
        assert self._printed_lines() == ['OK\n']


class WhenCasesFail(BaseFixture):
    def setup(self):
        super(WhenCasesFail, self).setup()
        suite = Dingus(success=False)
        QuietPrinter(suite).print_result()

    def should_print_failure_message(self):
        assert self._printed_lines() == ['Specs failed\n']

