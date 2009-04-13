import os
import unittest
from optparse import OptionParser
import sys
from itertools import chain, count
import re
import traceback

from mote.localfunctions import LocalFunctions


class DummyTestCase(unittest.TestCase):
    def nop(self):
        pass


def raises(exception, callable_, *args, **kwargs):
    try:
        assert_raises = DummyTestCase('nop').failUnlessRaises
        assert_raises(exception, callable_, *args, **kwargs)
    except AssertionError:
        return False
    else:
        return True


DEFAULT_GLOBALS = dict(raises=raises)


class SpecSuite:
    def __init__(self, contents_of_modules):
        self.contexts = [
            ctx
            for module_contents in contents_of_modules
            for ctx in self._contexts_from_module(module_contents.values())]
        self.success = all(ctx.success for ctx in self.contexts)

    def _contexts_from_module(self, module_contents):
        return [Context(value)
                for value in module_contents
                if callable(value)
                and value.__name__.startswith('describe_')]


class ImportedModule(dict):
    def __init__(self, filename):
        self.update(DEFAULT_GLOBALS)
        execfile(filename, self)


class Case:
    def __init__(self, context, name):
        self.context = context
        self.name = name
        self.pretty_name = name.replace('_', ' ')
        self._run()

    def _run(self):
        case_function = self.context.fresh_function_named(self.name)
        try:
            case_function()
        except Exception, e:
            self.failure = Failure(sys.exc_info())
            self.success = False
            self.exception = e
        else:
            self.success = True


class Failure:
    def __init__(self, exc_info):
        self.exc_type, self.exc_value, self.exc_traceback = exc_info
        self.exception_line = self.exc_traceback.tb_next.tb_lineno

    def format_exception(self):
        traceback_lines = traceback.format_exception(
            self.exc_type,
            self.exc_value,
            self.exc_traceback.tb_next)
        return '\n%s\n' % ''.join(traceback_lines)


class PythonFilesInDirectory(list):
    def __init__(self, parent):
        if not os.path.isdir(parent):
            self._extend_with_file(parent)
        else:
            self._extend_with_directory(parent)

    def _extend_with_file(self, path):
        if path.endswith('.py'):
            self.append(path)

    def _extend_with_directory(self, path):
        for child in os.listdir(path):
            child_path = os.path.join(path, child)
            self.extend(PythonFilesInDirectory(child_path))

class Context:
    def __init__(self, context_function, parent=None):
        self.original_context_function = context_function
        self.parent = parent
        self.name = context_function.__name__
        self.pretty_name = self.name.replace('_', ' ')
        self.cases = self._collect_cases()
        self.contexts = self._collect_contexts()
        self.success = (all(case.success for case in self.cases)
                        and
                        all(ctx.success for ctx in self.contexts))

    @property
    def context_function(self):
        if self.parent:
            return self.parent.fresh_function_named(self.name)
        else:
            return self.original_context_function

    def _collect_contexts(self):
        local_functions = LocalFunctions.context_functions(
            self.context_function)
        return [Context(function, self) for function in local_functions]

    def _collect_cases(self):
        case_functions = LocalFunctions.case_functions(self.context_function)
        cases = [Case(self, case_function.__name__)
                 for case_function in case_functions]
        return cases

    def fresh_function_named(self, name):
        local_functions = LocalFunctions(self.context_function)
        return local_functions.function_with_name(name)


class ResultPrinter:
    PADDING_PER_LINE = '  '

    def __init__(self, contexts):
        self._print_contexts(contexts, '')

    def _failing_case_status(self, case):
        exception_name = case.exception.__class__.__name__
        failure = case.failure
        return ' -> FAIL (%s @ %i)' % (exception_name,
                                       failure.exception_line)

    def _print_cases(self, cases, padding):
        failure_numbers = count(1)

        for case in cases:
            if case.success:
                result = ''
            else:
                case.failure.number = failure_numbers.next()
                result = self._failing_case_status(case)

            sys.stdout.write('%s  - %s%s\n' % (padding,
                                               case.pretty_name,
                                               result))

            if not case.success:
                sys.stdout.write(case.failure.format_exception())

    def _print_contexts(self, contexts, padding):
        for context in contexts:
            sys.stdout.write('%s%s\n' % (padding,
                                         context.pretty_name))
            self._print_cases(context.cases, padding)
            self._print_contexts(context.contexts,
                                 padding + self.PADDING_PER_LINE)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-q', '--quiet', action='store_true', dest='quiet')
    options, args = parser.parse_args()

    suite = SpecSuite(map(ImportedModule,
                          PythonFilesInDirectory(args[0])))
    if not options.quiet:
        ResultPrinter(suite.contexts)

    if suite.success:
        print 'All specs passed'
    else:
        print 'Specs failed'

