from faker import Faker
from survey.survey_schedule import SurveySchedule
from edc_base.utils import get_utcnow
from dateutil.relativedelta import relativedelta
# from survey.site_surveys import site_surveys

fake = Faker()


class SurveyMixin():

    def make_survey_schedule(self, group_name=None, name=None, **options):
        return SurveySchedule(
            name=name or fake.safe_color_name(),
            group_name=group_name or 'test_survey',
            start=(get_utcnow() - relativedelta(years=5)),
            end=(get_utcnow() - relativedelta(years=1)),
            **options)

        # site_surveys.register(survey_schedule)
