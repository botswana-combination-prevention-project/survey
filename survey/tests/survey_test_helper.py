from dateutil.relativedelta import relativedelta
from faker import Faker

from edc_base.utils import get_utcnow

from ..survey_schedule import SurveySchedule
from .load_test_surveys import load_test_surveys

fake = Faker()


class SurveyTestHelperError(Exception):
    pass


class SurveyTestHelper:

    def load_test_surveys(self, **kwargs):
        load_test_surveys(**kwargs)

    def make_survey_schedule(self, group_name=None, name=None, **options):
        return SurveySchedule(
            name=name or fake.safe_color_name(),
            group_name=group_name or 'test_survey',
            start=(get_utcnow() - relativedelta(years=5)),
            end=(get_utcnow() - relativedelta(years=1)),
            **options)
