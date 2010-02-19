from sys import stdout
import sys
from mote import suite


class SpecOutputPrinter:
    INDENT = ' ' * 2

    def print_suite(self, suite):
        self._print_contexts(suite.contexts)
        QuietPrinter().print_suite(suite)

    def _failing_context_status(self, context):
        exception_name = context.exception.__class__.__name__
        failure = context.failure
        return ' -> FAIL (%s @ %i)' % (exception_name,
                                       failure.exception_line)

    def _print_case(self, context):
        if context.success:
            result = ''
        else:
            result = self._failing_context_status(context)

        stdout.write('%s- %s%s\n' % (self.INDENT,
                                     context.pretty_name,
                                     result))

        if not context.success:
            stdout.write('\n%s\n' % context.failure.formatted_exception)

    def _print_contexts(self, contexts):
        for context in contexts:
            if context.has_cases:
                stdout.write('%s\n' % context.pretty_name)

            if context.children:
                self._print_contexts(context.children)
            else:
                self._print_case(context)

    def handle_import_failure(self, exc_info):
        raise


class QuietPrinter:
    def print_suite(self, suite):
        message = 'OK' if suite.success else 'Specs failed'
        stdout.write('%s\n' % message)

    def handle_import_failure(self, exc_info):
        raise


class MachineOutputPrinter:
    def print_suite(self, suite):
        self._print_contexts(suite.contexts)

    def _print_contexts(self, contexts):
        for context in contexts:
            self._print_context(context)

    def _print_context(self, context):
        if context.is_case and not context.success:
            self.print_failure(context.filename,
                               context.name,
                               context.failure)
        if context.children:
            self._print_contexts(context.children)

    def print_failure(self, filename, function_name, failure):
        stdout.write('%s: In %s\n' % (filename, function_name))
        stdout.write('%s:%s: error: %s\n' % (
            filename,
            failure.exception_line,
            failure.exception_description))

    def handle_import_failure(self, exc_info):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback = self._deepest_level_of_traceback(exc_traceback)
        failure = suite.Failure((exc_type, exc_value, traceback))
        tb = failure.exc_traceback
        filename = tb.tb_frame.f_code.co_filename
        self.print_failure(filename, '<module>', failure)

    def _deepest_level_of_traceback(self, traceback):
        while traceback.tb_next:
            traceback = traceback.tb_next
        return traceback

