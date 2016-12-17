# coding=utf-8

from dateutil.relativedelta import relativedelta

from edc_base.utils import get_utcnow

from .site_surveys import site_surveys
from .survey import Survey
from .survey_schedule import SurveySchedule


survey_one = SurveySchedule(
    name='survey-1',
    start_datetime=get_utcnow() - relativedelta(years=1),
    end_datetime=get_utcnow())

survey = Survey(
    map_area='test_community',
    start_datetime=get_utcnow() - relativedelta(years=1),
    end_datetime=get_utcnow(),
    full_enrollment_datetime=get_utcnow() - relativedelta(weeks=1)
)

survey_one.add_survey(survey)

# SurveySchedule(name='bcpp-year-2')
# SurveySchedule(name='bcpp-year-3')

site_surveys.register(survey_one)
