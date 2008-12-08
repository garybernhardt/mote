from optparse import OptionParser
import sys


class LocalFunctions(list):
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
        local_functions = self._local_functions_in_frame(frame)
        self.extend(local_functions)

    def _trace_function_call(self, frame):
        traced_fn_name = frame.f_code.co_name
        if traced_fn_name == self.function.__name__:
            return self._trace
        else:
            return None

    @staticmethod
    def _local_functions_in_frame(frame):
        return [local_obj
                for name, local_obj in frame.f_locals.items()
                if callable(local_obj)]

    def function_with_name(self, name):
        return [function
                for function in self
                if function.__name__ == name][0]


class SortedFunctions(list):
    def __init__(self, functions):
        self.extend(sorted(functions,
                           key=lambda fn: fn.func_code.co_firstlineno))


class CasesFromContexts(list):
    def __init__(self, contexts):
        for context in contexts:
            for case in context.cases:
                self.append(case)


class ContextsFromModule(list):
    def __init__(self, module_contents):
        self.extend(Context(attribute)
                    for attribute in module_contents
                    if callable(attribute)
                    and attribute.__name__.startswith('describe_'))


class SpecSuite:
    def __init__(self, module_contents):
        self.module_contents = module_contents.values()
        self.contexts = ContextsFromModule(self.module_contents)

    def run(self):
        return list(self._run_contexts())

    def _run_contexts(self):
        cases = CasesFromContexts(self.contexts)
        for case in cases:
            yield case
            if not case.success:
                self.success = False
                return
        self.success = True


class ImportedModule(dict):
    def __init__(self, filename):
        execfile(filename, self)


class Case:
    def __init__(self, context_function, name):
        self.name = name
        self.pretty_name = name.replace('_', ' ')
        local_functions = LocalFunctions(context_function)
        self.case_function = local_functions.function_with_name(name)
        self._run()

    def _run(self):
        try:
            self.case_function()
        except Exception, e:
            exc_type, exc_value, traceback = sys.exc_info()
            self.exception_line = traceback.tb_next.tb_lineno
            self.success = False
            self.exception = e
        else:
            self.success = True


class Context:
    def __init__(self, context_function):
        self.context_function = context_function
        self.name = context_function.__name__
        self.pretty_name = self.name.replace('_', ' ')
        self.cases = self._collect_cases()

    def _collect_cases(self):
        case_functions = LocalFunctions(self.context_function)
        case_functions = SortedFunctions(case_functions)
        cases = [Case(self.context_function,
                      case_function.__name__)
                 for case_function in case_functions]
        return cases


class ResultPrinter:
    def __init__(self, contexts):
        for context in contexts:
            sys.stdout.write('%s\n' % context.pretty_name)
            for case in context.cases:
                if case.success:
                    status = 'ok'
                else:
                    status = 'FAIL (%s @ %i)' % (
                        case.exception.__class__.__name__,
                        case.exception_line)
                sys.stdout.write('  %s -> %s\n' % (case.pretty_name, status))


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-q', '--quiet', action='store_true', dest='quiet')
    options, args = parser.parse_args()

    suite = SpecSuite(ImportedModule(args[0]))
    suite.run()
    if not options.quiet:
        ResultPrinter(suite.contexts)

    if suite.success:
        print 'All specs passed'
    else:
        print 'Specs failed'

