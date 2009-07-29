import sys

from nose.tools import assert_raises
from dingus import Dingus, DingusTestCase

import mote.printers as mod
from mote.printers import QuietPrinter
from tests.unit.patchedstdout import PatchedStdoutMixin


class BaseFixture(DingusTestCase(QuietPrinter),
                  PatchedStdoutMixin(mod)):
    pass

class WhenCasesPass(BaseFixture):
    def setup(self):
        super(WhenCasesPass, self).setup()
        suite = Dingus(success=True)
        QuietPrinter().print_suite(suite)

    def should_print_ok(self):
        assert self._printed_lines() == ['OK\n']


class WhenCasesFail(BaseFixture):
    def setup(self):
        super(WhenCasesFail, self).setup()
        suite = Dingus(success=False)
        QuietPrinter().print_suite(suite)

    def should_print_failure_message(self):
        assert self._printed_lines() == ['Specs failed\n']


class WhenHandlingImportErrors(BaseFixture):
    class FakeError(Exception):
        pass

    def should_reraise_errors(self):
        assert_raises(self.FakeError, self._handle_error)

    def _handle_error(self):
        printer = QuietPrinter()
        try:
            raise self.FakeError
        except self.FakeError:
            printer.handle_import_failure(sys.exc_info())

