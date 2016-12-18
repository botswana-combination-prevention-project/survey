from faker import Faker
from survey.survey_schedule import SurveySchedule
from edc_base.utils import get_utcnow
from dateutil.relativedelta import relativedelta
# from survey.site_surveys import site_surveys

fake = Faker()


class SurveyMixin():

    def make_survey_schedule(self):
        return SurveySchedule(
            name=fake.safe_color_name,
            start_date=(get_utcnow() - relativedelta(years=5)).date(),
            end_date=(get_utcnow() - relativedelta(years=1)).date())

        # site_surveys.register(survey_schedule)
