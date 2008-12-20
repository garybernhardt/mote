from dingus import Dingus, DingusTestCase
import mote
from mote import CasesFromContexts


class WhenGivenContexts(DingusTestCase(CasesFromContexts)):
    def setup(self):
        super(WhenGivenContexts, self).setup()
        self.case = Dingus()
        context = Dingus(cases=[self.case],
                         contexts=[])
        self.cases = CasesFromContexts([context])

    def should_get_cases_from_contexts(self):
        assert self.cases == [self.case]


class WhenContextsHaveNestedContexts(DingusTestCase(CasesFromContexts)):
    def setup(self):
        super(WhenContextsHaveNestedContexts, self).setup()
        self.case = Dingus()
        mote.CasesFromContexts = Dingus()
        mote.CasesFromContexts.return_value = [self.case]
        context = Dingus(cases=[],
                         contexts=[Dingus()])
        self.cases = CasesFromContexts([context])

    def should_find_nested_cases(self):
        assert self.cases == [self.case]

