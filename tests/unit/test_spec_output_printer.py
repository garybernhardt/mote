import sys

from dingus import Dingus, DingusTestCase
import mote
from mote import SpecOutputPrinter


class WithPatchedStdOut(DingusTestCase(SpecOutputPrinter, 'count')):
    def setup(self):
        super(WithPatchedStdOut, self).setup()
        mote.sys = Dingus()

    def _wrote(self, text):
        return mote.sys.stdout.calls('write', text).one()


class WhenCasesPass(WithPatchedStdOut):
    def setup(self):
        super(WhenCasesPass, self).setup()
        self.case = Dingus(pretty_name='should frob', children=[])
        self.context = Dingus(pretty_name='frobber',
                              children=[self.case])
        SpecOutputPrinter([self.context])

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
                            failure=Dingus(
                                exception_line=3,
                                formatted_exception='traceback1'),
                            children=[])
        self.case2 = Dingus(pretty_name='should 2',
                            success=False,
                            exception=AssertionError(),
                            failure=Dingus(
                                exception_line=5,
                                formatted_exception='traceback2'),
                            children=[])
        self.context = Dingus(pretty_name='describe frobber',
                              children=[self.case1, self.case2])
        SpecOutputPrinter([self.context])

    def should_print_failure_message(self):
        assert self._wrote('  - should 1 -> FAIL (AssertionError @ 3)\n')
        assert self._wrote('  - should 2 -> FAIL (AssertionError @ 5)\n')

    def should_print_traceback(self):
        assert self._wrote('\ntraceback1\n')
        assert self._wrote('\ntraceback2\n')


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
        SpecOutputPrinter([outer_context])

    def should_combine_context_names(self):
        assert self._wrote('outer context inner context\n')

    def shouldnt_print_anything_else(self):
        printed_lines = [call.args[0]
                         for call in mote.sys.stdout.calls('write')]
        assert set(printed_lines) == set(['outer context inner context\n',
                                          '  - case\n'])

