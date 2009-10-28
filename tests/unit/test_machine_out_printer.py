import sys

from dingus import Dingus, DingusTestCase, exception_raiser
import mote.printers as mod
from mote import Failure
from mote.printers import MachineOutputPrinter
from tests.unit.patchedstdout import PatchedStdoutMixin


class BaseFixture(DingusTestCase(MachineOutputPrinter),
                  PatchedStdoutMixin(mod)):
    pass


class WhenCaseFails(BaseFixture):
    def setup(self):
        super(WhenCaseFails, self).setup()
        failure = Dingus(exception_line=123,
                         exception_description='exception description')
        context = Dingus(is_case=True,
                         success=False,
                         filename='filename.py',
                         failure=failure,
                         children=[])
        context.name = 'some_context'
        suite = Dingus(contexts=[context])
        MachineOutputPrinter().print_suite(suite)

    def should_print_error(self):
        assert self._printed_lines() == [
            'filename.py: In some_context\n',
            'filename.py:123: error: exception description\n']


class WhenParentContextFails(BaseFixture):
    def setup(self):
        super(WhenParentContextFails, self).setup()
        context = Dingus(is_case=False,
                         success=False,
                         children=[])
        suite = Dingus(contexts=[context])
        MachineOutputPrinter().print_suite(suite)

    def should_not_print_anything(self):
        assert self._printed_lines() == []


class WhenNestedCaseFails(BaseFixture):
    def setup(self):
        super(WhenNestedCaseFails, self).setup()
        failure = Dingus(exception_line=123,
                         exception_description='exception description')
        child = Dingus('child',
                       is_case=True,
                       success=False,
                       filename='filename.py',
                       failure=failure,
                       children=[])
        child.name = 'some_context'
        parent = Dingus('parent',
                        is_case=False,
                        children=[child])
        suite = Dingus(contexts=[parent])
        MachineOutputPrinter().print_suite(suite)

    def should_print_error(self):
        assert self._printed_lines() == [
            'filename.py: In some_context\n',
            'filename.py:123: error: exception description\n']


class WhenContextSucceeds(BaseFixture):
    def setup(self):
        super(WhenContextSucceeds, self).setup()
        context = Dingus(success=True,
                         children=[])
        suite = Dingus(contexts=[context])
        MachineOutputPrinter().print_suite(suite)

    def should_not_print_anything(self):
        assert self._printed_lines() == []


class WhenPrintingAFailure(DingusTestCase(MachineOutputPrinter,
                                          exclude=['sys',
                                                   'dirname',
                                                   'abspath',
                                                   '__file__',
                                                   'mote',
                                                   'traceback']),
                           PatchedStdoutMixin(mod)):
    def setup(self):
        super(WhenPrintingAFailure, self).setup()

        class FakeError(Exception):
            pass
        def outer_function():
            inner_function()
        def inner_function():
            raise FakeError

        try:
            outer_function()
        except FakeError, e:
            exc_info = sys.exc_info()

        self.failure_line = inner_function.func_code.co_firstlineno + 1
        MachineOutputPrinter().handle_import_failure(exc_info)

    def should_print_the_exception(self):
        this_file = __file__.replace('.pyc', '.py')
        assert self._printed_lines() == [
            '%s: In <module>\n' % this_file,
            '%s:%i: error: FakeError\n' % (this_file, self.failure_line)]

