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


class SpecSuite:
    def __init__(self, module_contents):
        self.module_contents = module_contents.values()

    def run(self):
        return list(self._run_contexts(self.module_contents))

    def _run_contexts(self, module_contents):
        cases = CasesFromContexts(list(self._contexts()))
        for case in cases:
            yield case
            if not case.success:
                self.success = False
                return
        self.success = True

    def _contexts(self):
        for context_function in self._context_functions():
            yield Context(context_function)

    def _context_functions(self):
        return [module_attribute
                for module_attribute in self.module_contents
                if callable(module_attribute)]


class ImportedModule(dict):
    def __init__(self, filename):
        execfile(filename, self)


class Case:
    def __init__(self, context_function, case_name):
        self.case_name = case_name
        local_functions = LocalFunctions(context_function)
        self.case_function = local_functions.function_with_name(case_name)
        self._run()

    def _run(self):
        try:
            self.case_function()
        except:
            self.success = False
        else:
            self.success = True


class Context:
    def __init__(self, context_function):
        self.context_function = context_function
        self.cases = self._collect_cases()

    def _collect_cases(self):
        case_functions = LocalFunctions(self.context_function)
        case_functions = SortedFunctions(case_functions)
        cases = [Case(self.context_function,
                      case_function.__name__)
                 for case_function in case_functions]
        return cases


if __name__ == '__main__':
    suite = SpecSuite(ImportedModule(sys.argv[1]))
    suite.run()
    if suite.success:
        print 'All specs passed'
    else:
        print 'Specs failed'

