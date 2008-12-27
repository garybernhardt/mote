import os
import unittest
from optparse import OptionParser
import sys
from itertools import chain


class DummyTestCase(unittest.TestCase):
    def nop(self):
        pass

DEFAULT_GLOBALS = dict(assert_raises=DummyTestCase('nop').failUnlessRaises)


class FunctionLocals(list):
    def __init__(self, function):
        self.function = function
        self._call_function_with_trace()

    def _call_function_with_trace(self):
        sys.settrace(self._trace)
        self.function()
        sys.settrace(None)

    def _trace(self, frame, event, arg):
        if event == 'return':
            self._trace_return_statement(frame)
        elif event == 'call':
            trace_function_for_function = self._trace_function_call(frame)
            return trace_function_for_function

    def _trace_return_statement(self, frame):
        self.extend(frame.f_locals.values())

    def _trace_function_call(self, frame):
        traced_fn_name = frame.f_code.co_name
        if traced_fn_name == self.function.__name__:
            return self._trace
        else:
            return None


class LocalFunctions(list):
    def __init__(self, function, prefix):
        self.function = function
        self.prefix = prefix
        self.extend(self._local_functions_in_frame())

    @classmethod
    def case_functions(cls, context_function):
        return cls(context_function, 'should_')

    @classmethod
    def context_functions(cls, context_function):
        return cls(context_function, 'when_')

    def _local_functions_in_frame(self):
        return [local_obj
                for local_obj
                in FunctionLocals(self.function)
                if callable(local_obj)
                and local_obj.__name__.startswith(self.prefix)]

    def function_with_name(self, name):
        return [function
                for function in self
                if function.__name__ == name][0]


class SortedFunctions(list):
    def __init__(self, functions):
        self.extend(sorted(functions,
                           key=lambda fn: fn.func_code.co_firstlineno))


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
            exc_type, exc_value, traceback = sys.exc_info()
            self.exception_line = traceback.tb_next.tb_lineno
            self.success = False
            self.exception = e
        else:
            self.success = True


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
        self.context_function = context_function
        self.parent = parent
        self.name = context_function.__name__
        self.pretty_name = self.name.replace('_', ' ')
        self.cases = self._collect_cases()
        self.contexts = self._collect_contexts()
        self.success = (all(case.success for case in self.cases)
                        and
                        all(ctx.success for ctx in self.contexts))

    def _collect_contexts(self):
        local_functions = LocalFunctions.context_functions(
            self.context_function)
        sorted_functions = SortedFunctions(local_functions)
        return [Context(function, self) for function in sorted_functions]

    def _collect_cases(self):
        case_functions = LocalFunctions.case_functions(self.context_function)
        case_functions = SortedFunctions(case_functions)
        cases = [Case(self, case_function.__name__)
                 for case_function in case_functions]
        return cases

    def fresh_function_named(self, name):
        if self.parent is None:
            context_function = self.context_function
        else:
            context_function = self.parent.fresh_function_named(self.name)
        local_functions = LocalFunctions(context_function, name)
        return local_functions.function_with_name(name)


class ResultPrinter:
    PADDING_PER_LINE = '  '

    def __init__(self, contexts):
        self._print_contexts(contexts, '')

    def _case_status(self, case):
        if case.success:
            return 'ok'
        else:
            exception_name = case.exception.__class__.__name__
            exception_line = case.exception_line
            return 'FAIL (%s @ %i)' % (exception_name, exception_line)

    def _print_cases(self, cases, padding):
        for case in cases:
            sys.stdout.write('%s  %s -> %s\n' % (padding,
                                                 case.pretty_name,
                                                 self._case_status(case)))

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

