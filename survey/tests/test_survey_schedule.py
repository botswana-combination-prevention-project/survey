# coding=utf-8

from dateutil.relativedelta import relativedelta

from django.test import TestCase, tag

from edc_base.utils import get_utcnow

from ..exceptions import SurveyDateError
from ..exceptions import SurveyScheduleError
from ..survey_schedule import SurveySchedule
from .survey_test_helper import SurveyTestHelper


class TestSurvey(TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()

    def test_schedule_good_dates(self):
        try:
            SurveySchedule(
                name='survey-1',
                start=(get_utcnow() - relativedelta(years=1)),
                end=get_utcnow())
        except SurveyScheduleError as e:
            self.fail(
                'SurveyScheduleError unexpectedly raised. Got {}'.format(e))

    def test_schedule_bad_dates(self):
        try:
            SurveySchedule(
                name='survey-1',
                start=get_utcnow(),
                end=(get_utcnow() - relativedelta(years=1)))
            self.fail('SurveyDateError unexpectedly NOT raised')
        except SurveyDateError:
            pass
