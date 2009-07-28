import sys
import textwrap

from dingus import Dingus, DingusTestCase, exception_raiser, DontCare

import mote as mod
from mote import Failure, Context


class FakeError(Exception):
    pass


def some_function():
    raise FakeError


def some_other_function():
    raise FakeError


EXPECTED_TRACEBACK = textwrap.dedent(
    """\
    Traceback (most recent call last):
      File "%s", line 15, in some_function
        raise FakeError
    FakeError
    """ % __file__.replace('.pyc', '.py'))


class DescribeFailureWhenMoteModuleIsntInvolved:
    def _failure_for_function(self, function):
        try:
            function()
        except FakeError:
            exc_type, exc_value, exc_traceback = sys.exc_info()

        # Remove this setup method from the traceback for simplicity
        exc_traceback = exc_traceback.tb_next

        return Failure((exc_type, exc_value, exc_traceback))

    def should_have_traceback_line_number(self):
        failure = self._failure_for_function(some_function)
        assert failure.exception_line == 15
        failure = self._failure_for_function(some_other_function)
        assert failure.exception_line == 19

    def should_format_exception(self):
        failure = self._failure_for_function(some_function)
        assert failure.formatted_exception == EXPECTED_TRACEBACK


class DescribeFailureWhenMoteModuleIsInvolved:
    def setup(self):
        context = Context(some_function)
        self.failure = context.failure

    def should_have_traceback_line_number(self):
        assert self.failure.exception_line == 15

    def should_exclude_mote_internals_from_traceback(self):
        assert self.failure.formatted_exception in EXPECTED_TRACEBACK

