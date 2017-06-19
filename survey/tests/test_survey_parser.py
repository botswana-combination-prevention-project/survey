# coding=utf-8

from django.test import TestCase, tag

from ..exceptions import SurveyError
from ..sparser import S
from .survey_test_helper import SurveyTestHelper


class TestSurveyParser(TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()

    def test_s_parser_raises1(self):
        s = 'ess'
        self.assertRaises(SurveyError, S, s)

        s = 'bcpp_survey.ess'
        self.assertRaises(SurveyError, S, s)

    def test_s_parse_survey_schedule(self):
        s = 'bcpp_survey.year-1.test_community'
        s = S(s)
        self.assertEqual(s.group_name, 'bcpp_survey')
        self.assertEqual(s.survey_schedule_name, 'year-1')
        self.assertEqual(s.map_area, 'test_community')
        self.assertEqual(s.survey_field_value, None)
        self.assertEqual(
            s.survey_schedule_field_value, 'bcpp_survey.year-1.test_community')
        self.assertEqual(s.field_value, 'bcpp_survey.year-1.test_community')

    def test_s_parse_survey_schedule_with_survey(self):
        s = 'bcpp_survey.year-1.test_community'
        s = S(s, 'ess')
        self.assertEqual(s.group_name, 'bcpp_survey')
        self.assertEqual(s.survey_schedule_name, 'year-1')
        self.assertEqual(s.survey_name, 'ess')
        self.assertEqual(s.map_area, 'test_community')
        self.assertEqual(
            s.survey_field_value, 'bcpp_survey.year-1.ess.test_community')
        self.assertEqual(
            s.survey_schedule_field_value, 'bcpp_survey.year-1.test_community')
        self.assertEqual(s.field_value, 'bcpp_survey.year-1.test_community')

    def test_s_parse_survey(self):
        s = 'bcpp_survey.year-1.ess.test_community'
        s = S(s)
        self.assertEqual(s.group_name, 'bcpp_survey')
        self.assertEqual(s.survey_schedule_name, 'year-1')
        self.assertEqual(s.survey_name, 'ess')
        self.assertEqual(s.map_area, 'test_community')
        self.assertEqual(
            s.survey_field_value, 'bcpp_survey.year-1.ess.test_community')
        self.assertEqual(
            s.survey_schedule_field_value, 'bcpp_survey.year-1.test_community')
        self.assertEqual(
            s.field_value, 'bcpp_survey.year-1.ess.test_community')
