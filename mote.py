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


class SpecSuite:
    def __init__(self, module_path):
        self.function = function

    @property
    def local_objects(self):
        function_locals = dict()
        def trace(frame, event, arg):
            traced_fn_name = frame.f_code.co_name
            if event == 'return':
                function_locals[traced_fn_name] = frame.f_locals
            elif event == 'call':
                if traced_fn_name == self.function.__name__:
                    return trace

        sys.settrace(trace)
        self.function()
        sys.settrace(None)

        return function_locals[self.function.__name__]

    def run(self):
        name = self.function.__name__
        for name, child in self.sorted_children:
            Case(child).run()


class SpecSuite:
    def __init__(self, module_contents):
        self.module_contents = module_contents.values()

    def run(self):
        self._run_contexts(self.module_contents)

    def _context_functions_in_module(self, module_contents):
        return [module_attribute
                for module_attribute in module_contents
                if callable(module_attribute)]

    def _run_contexts(self, module_contents):
        context_functions = self._context_functions_in_module(module_contents)
        for context_function in context_functions:
            context = Context(context_function)
            context.run()
            if not context.success:
                self.success = False
                return
        else:
            self.success = True


class ImportedModule(dict):
    def __init__(self, filename):
        execfile(filename, self)


class Context:
    def __init__(self, context_function):
        self.context_function = context_function

    def run(self):
        try:
            self._run_all_cases()
        except:
            self.success = False
        else:
            self.success = True

    def _run_all_cases(self):
        case_functions = LocalFunctions(self.context_function)
        sorted_case_functions = sorted(
            case_functions,
            key=lambda fn: fn.func_code.co_firstlineno)
        for case_function in sorted_case_functions:
            case_function()


if __name__ == '__main__':
    suite = SpecSuite(ImportedModule(sys.argv[1]))
    suite.run()
    if suite.success:
        print 'All specs passed'
    else:
        print 'Specs failed'

