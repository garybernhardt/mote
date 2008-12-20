from dingus import Dingus, DingusTestCase
import mote
from mote import SortedFunctions


BaseFixture = DingusTestCase(SortedFunctions)


class WhenExaminingFunctionWithMultipleLocalFunctions(BaseFixture):
    def setup(self):
        super(WhenExaminingFunctionWithMultipleLocalFunctions, self).setup()
        self.func1, self.func2 = Dingus.many(2)
        self.func1.func_code.co_firstlineno = 1
        self.func2.func_code.co_firstlineno = 2
        self.functions = [self.func1, self.func2]

    def should_sort_functions(self):
        functions = SortedFunctions(self.functions)
        assert functions == [self.func1, self.func2]

    def should_sort_functions_when_reversed(self):
        functions = SortedFunctions(list(reversed(self.functions)))
        assert functions == [self.func1, self.func2]

