# coding=utf-8

from dateutil.relativedelta import relativedelta

from django.test import TestCase, tag

from edc_base.utils import get_utcnow

from ..site_surveys import site_surveys
from ..survey_schedule import SurveySchedule, SurveyScheduleError
from .survey_test_helper import SurveyTestHelper
from .surveys import survey_one, survey_two, survey_three
from pprint import pprint


class TestSurveySchedule(TestCase):

    survey_helper = SurveyTestHelper()

    def test_schedule_good_dates(self):
        try:
            SurveySchedule(
                name='survey-1',
                start=(get_utcnow() - relativedelta(years=1)),
                end=get_utcnow())
        except SurveyScheduleError as e:
            self.fail(
                f'SurveyScheduleError unexpectedly raised. Got {e}')

    def test_schedule_bad_dates(self):
        self.assertRaises(
            SurveyScheduleError,
            SurveySchedule,
            name='survey-1',
            start=get_utcnow(),
            end=(get_utcnow() - relativedelta(years=1)))

    def test_get_survey_schedule_current(self):
        self.survey_helper.load_test_surveys(
            load_all=True, current_survey_index=0)
        self.assertEqual(
            survey_one.field_value,
            site_surveys.get_survey_schedules(current=True)[0].field_value)

    def test_get_survey_schedule_current2(self):
        self.survey_helper.load_test_surveys(
            load_all=True, current_survey_index=1)
        self.assertEqual(
            survey_two.field_value,
            site_surveys.get_survey_schedules(current=True)[0].field_value)

    def test_get_survey_schedule_current3(self):
        self.survey_helper.load_test_surveys(
            load_all=True, current_survey_index=2)
        self.assertEqual(
            survey_three.field_value,
            site_surveys.get_survey_schedules(current=True)[0].field_value)
