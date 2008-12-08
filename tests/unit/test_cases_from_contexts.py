from dingus import Dingus, DingusFixture
import mote
from mote import CasesFromContexts


class WhenGivenContexts(DingusFixture(CasesFromContexts)):
    def setup(self):
        super(WhenGivenContexts, self).setup()
        self.case = Dingus()
        context = Dingus(cases=[self.case])
        self.cases = CasesFromContexts([context])

    def should_get_cases_from_contexts(self):
        assert self.cases == [self.case]

