from dingus import Dingus, DingusFixture
import mote
from mote import CaseResult


class WhenCasePasses(DingusFixture(CaseResult)):
    def setup(self):
        super(WhenCasePasses, self).setup()
        self.case_name = Dingus()
        self.case_result = CaseResult.success(self.case_name)

    def should_have_success_flag(self):
        assert self.case_result.success


class WhenCaseFails(DingusFixture(CaseResult)):
    def setup(self):
        super(WhenCaseFails, self).setup()
        self.case_name = Dingus()
        self.case_result = CaseResult.failure(self.case_name)

    def should_not_have_success_flag(self):
        assert not self.case_result.success

