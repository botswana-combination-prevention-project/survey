# coding=utf-8

from django.test import TestCase, tag

from ..iterators import SurveyScheduleIterator
from ..site_surveys import site_surveys
from .surveys import survey_one, survey_two, survey_three
from .survey_test_helper import SurveyTestHelper


class TestSurvey(TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys(load_all=True)

    def test_survey_schedule_iterator(self):
        survey_schedules = site_surveys.get_survey_schedules(
            group_name='test_survey')
        survey_schedule1 = survey_schedules[0]
        survey_schedule2 = survey_schedules[1]
        survey_schedule3 = survey_schedules[2]
        survey_schedule_iterator = SurveyScheduleIterator(
            survey_schedule=survey_schedule1)
        survey_schedule = next(survey_schedule_iterator)
        self.assertEqual(survey_schedule, survey_schedule2)
        survey_schedule = next(survey_schedule_iterator)
        self.assertEqual(survey_schedule, survey_schedule3)
        self.assertRaises(StopIteration, next, survey_schedule_iterator)

    def test_survey_schedule_as_list(self):
        survey_one_iterator = SurveyScheduleIterator(
            survey_schedule=survey_one)
        self.assertEqual(
            [s.field_value for s in list(survey_one_iterator)],
            [survey_two.field_value, survey_three.field_value])

    def test_survey_schedule_iterator_reversed(self):
        survey_one_iterator = SurveyScheduleIterator(
            survey_schedule=survey_one)
        result = []
        for survey_schedule in reversed(list(survey_one_iterator)):
            result.append(survey_schedule)
        self.assertEqual([s.field_value for s in result], [
                         survey_three.field_value, survey_two.field_value])
