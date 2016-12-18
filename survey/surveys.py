# coding=utf-8

import sys

from dateutil.relativedelta import relativedelta

from edc_base.utils import get_utcnow

from .site_surveys import site_surveys
from .survey import Survey
from .survey_schedule import SurveySchedule


if 'test' in sys.argv:
    survey_one = SurveySchedule(
        name='survey-1',
        start_date=(get_utcnow() - relativedelta(years=1)).date(),
        end_date=get_utcnow().date())

    survey = Survey(
        map_area='test_community',
        start_date=(get_utcnow() - relativedelta(years=1)).date(),
        end_date=get_utcnow().date(),
        full_enrollment_date=(get_utcnow() - relativedelta(weeks=1)).date()
    )

    survey_one.add_survey(survey)

    # SurveySchedule(name='bcpp-year-2')
    # SurveySchedule(name='bcpp-year-3')

    site_surveys.register(survey_one)
