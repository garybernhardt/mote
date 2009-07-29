import sys

from nose.tools import assert_raises
from dingus import Dingus, DingusTestCase

import mote
from mote import SpecOutputPrinter
from tests.unit.patchedstdout import PatchedStdoutMixin


class WithPatchedStdOut(DingusTestCase(SpecOutputPrinter,
                                       'count',
                                       'QuietPrinter'),
                        PatchedStdoutMixin(mote)):
    def setup(self):
        super(WithPatchedStdOut, self).setup()
        mote.sys = Dingus()


class WhenCasesPass(WithPatchedStdOut):
    def setup(self):
        super(WhenCasesPass, self).setup()
        case = Dingus(pretty_name='should frob',
                      children=[],
                      has_cases=False)
        context = Dingus(pretty_name='frobber',
                         children=[case])
        suite = Dingus(contexts=[context])
        SpecOutputPrinter().print_suite(suite)

    def should_print_context_names_and_status(self):
        assert self._printed_lines() == ['frobber\n',
                                         '  - should frob\n',
                                         'OK\n']


class WhenCasesFail(WithPatchedStdOut):
    def setup(self):
        super(WhenCasesFail, self).setup()
        case1 = Dingus(pretty_name='should 1',
                       success=False,
                       exception=AssertionError(),
                       failure=Dingus(
                           exception_line=3,
                           formatted_exception='traceback1'),
                       has_cases=False,
                       children=[])
        case2 = Dingus(pretty_name='should 2',
                       success=False,
                       exception=AssertionError(),
                       failure=Dingus(
                           exception_line=5,
                           formatted_exception='traceback2'),
                       has_cases=False,
                       children=[])
        context = Dingus(pretty_name='describe frobber',
                         children=[case1, case2])
        suite = Dingus(contexts=[context], success=False)
        SpecOutputPrinter().print_suite(suite)

    def should_print_context_names_and_status(self):
        expected = ['describe frobber\n',
                    '  - should 1 -> FAIL (AssertionError @ 3)\n',
                    '\ntraceback1\n',
                    '  - should 2 -> FAIL (AssertionError @ 5)\n',
                    '\ntraceback2\n',
                    'Specs failed\n']
        assert self._printed_lines() == expected


class WhenCasesAreInNestedContexts(WithPatchedStdOut):
    def setup(self):
        super(WhenCasesAreInNestedContexts, self).setup()
        case = Dingus('case',
                      pretty_name='case',
                      children=[],
                      has_cases=False)
        inner_context = Dingus('inner_context',
                               pretty_name='outer context inner context',
                               children=[case],
                               has_cases=True)
        outer_context = Dingus('outer_context',
                               pretty_name='outer context',
                               children=[inner_context],
                               has_cases=False)
        suite = Dingus(contexts=[outer_context])
        SpecOutputPrinter().print_suite(suite)

    def should_combine_context_names(self):
        assert self._wrote('outer context inner context\n')

    def shouldnt_print_anything_else(self):
        assert self._printed_lines() == ['outer context inner context\n',
                                         '  - case\n',
                                         'OK\n']


class WhenHandlingImportErrors(WithPatchedStdOut):
    class FakeError(Exception):
        pass

    def should_reraise_errors(self):
        assert_raises(self.FakeError, self._handle_error)

    def _handle_error(self):
        printer = SpecOutputPrinter()
        try:
            raise self.FakeError
        except self.FakeError:
            printer.handle_import_failure(sys.exc_info())

