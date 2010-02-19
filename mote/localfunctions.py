import sys
from types import FunctionType


class LocalFunctions(list):
    def __init__(self, function, name_filter_fn=None):
        self.function = function
        if name_filter_fn is None:
            self.name_filter_fn = lambda name: not name.startswith('_')
        else:
            self.name_filter_fn = name_filter_fn
        self.extend(self._local_functions_in_frame())

    @classmethod
    def case_functions(cls, context_function):
        return cls(context_function, cls._is_case_function)

    @staticmethod
    def _is_case_function(name):
        return (not name.startswith('_') and
                not name.startswith('describe_'))

    @classmethod
    def context_functions(cls, context_function):
        return cls(context_function, cls._is_context_function)

    @staticmethod
    def _is_context_function(name):
        return name.startswith('describe_')

    def _local_functions_in_frame(self):
        functions = [local_obj
                     for local_obj
                     in FunctionLocals(self.function)
                     if isinstance(local_obj, FunctionType)
                     and self.name_filter_fn(local_obj.__name__)]
        return sorted(functions,
                      key=lambda fn: fn.func_code.co_firstlineno)

    def function_with_name(self, name):
        return [function
                for function in self
                if function.__name__ == name][0]


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

