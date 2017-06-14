# coding=utf-8

from dateutil.relativedelta import relativedelta

from django.test import TestCase, tag

from edc_base.utils import get_utcnow

from ..exceptions import AddSurveyMapAreaError, SurveyDateError
from ..exceptions import SurveyError, AddSurveyDateError
from ..survey import Survey

from .mixins import SurveyMixin


class TestSurvey(SurveyMixin, TestCase):

    def test_create_survey(self):
        try:
            Survey(
                map_area='test_community',
                start=(get_utcnow() - relativedelta(years=1)),
                end=get_utcnow(),
                full_enrollment_datetime=(get_utcnow() - relativedelta(weeks=1)))
        except SurveyError:
            self.fail('SurveyError unexpectedly raised')

    def test_create_survey_with_end_precedes_start(self):
        """Assert start date precedes end date."""
        self.assertRaises(
            SurveyDateError, Survey,
            map_area='test_community',
            start=get_utcnow(),
            end=(get_utcnow() - relativedelta(years=1)),
            full_enrollment_datetime=(get_utcnow() - relativedelta(weeks=1))
        )

    def test_create_survey_with_bad_start_equals_end(self):
        """Assert start date not equal to end date."""
        self.assertRaises(
            SurveyError, Survey,
            map_area='test_community',
            start=get_utcnow(),
            end=get_utcnow(),
            full_enrollment_datetime=(get_utcnow() - relativedelta(weeks=1))
        )

    def test_create_survey_with_bad_enrollment_date(self):
        self.assertRaises(
            SurveyError, Survey,
            map_area='test_community',
            start=(get_utcnow() - relativedelta(years=2)),
            end=(get_utcnow() - relativedelta(years=1)),
            full_enrollment_datetime=get_utcnow()
        )

    def test_add_survey_to_schedule(self):
        survey_schedule = self.make_survey_schedule()
        survey = Survey(
            map_area='test_community',
            start=(get_utcnow() - relativedelta(years=4)),
            end=(get_utcnow() - relativedelta(years=2)),
            full_enrollment_datetime=(get_utcnow() - relativedelta(years=3))
        )
        survey_schedule.add_survey(survey)

    def test_add_survey_with_bad_dates(self):
        survey_schedule = self.make_survey_schedule()
        bad_start = survey_schedule.start - relativedelta(years=1)
        end = survey_schedule.end
        survey = Survey(
            map_area='test_community',
            start=bad_start,
            end=end,
            full_enrollment_datetime=end - relativedelta(weeks=1)
        )
        self.assertRaises(
            AddSurveyDateError, survey_schedule.add_survey, survey)

    def test_add_survey_with_bad_dates2(self):
        survey_schedule = self.make_survey_schedule()
        start = survey_schedule.start
        bad_end = survey_schedule.end + relativedelta(years=1)
        survey = Survey(
            map_area='test_community',
            start=start,
            end=bad_end,
            full_enrollment_datetime=start + relativedelta(weeks=1)
        )
        self.assertRaises(
            AddSurveyDateError, survey_schedule.add_survey, survey)

    def test_create_survey_with_map_areas(self):
        survey_schedule = self.make_survey_schedule(
            map_areas=['test_community'])
        self.assertEqual(survey_schedule.map_areas, ['test_community'])

    def test_survey_with_bad_map_area(self):
        survey_schedule = self.make_survey_schedule(
            map_areas=['test_community'])
        survey = Survey(
            map_area='blahblah',
            start=survey_schedule.start + relativedelta(days=1),
            end=survey_schedule.end - relativedelta(days=1),
            full_enrollment_datetime=survey_schedule.end - relativedelta(days=2))
        self.assertRaises(
            AddSurveyMapAreaError, survey_schedule.add_survey, survey)

    def test_survey_without_map_areas_raises(self):
        survey_schedule = self.make_survey_schedule(map_areas=None)
        survey = Survey(
            map_area='blahblah',
            start=survey_schedule.start + relativedelta(days=1),
            end=survey_schedule.end - relativedelta(days=1),
            full_enrollment_datetime=survey_schedule.end - relativedelta(days=2))
        self.assertRaises(
            AddSurveyMapAreaError,
            survey_schedule.add_survey, survey)

    def test_get_survey_by_map_area(self):
        survey_schedule = self.make_survey_schedule()
        survey = Survey(
            map_area='test_community',
            start=survey_schedule.start + relativedelta(days=1),
            end=survey_schedule.end - relativedelta(days=1),
            full_enrollment_datetime=survey_schedule.end - relativedelta(days=2))
        survey_schedule.add_survey(survey)
        self.assertEqual(
            [survey], survey_schedule.get_surveys(map_area='test_community'))

    def test_get_survey_by_reference_datetime(self):
        survey_schedule = self.make_survey_schedule()
        survey1 = Survey(
            map_area='test_community',
            start=survey_schedule.start + relativedelta(days=1),
            end=survey_schedule.start + relativedelta(days=50),
            full_enrollment_datetime=survey_schedule.start + relativedelta(days=30))
        survey2 = Survey(
            map_area='test_community',
            start=survey_schedule.start + relativedelta(days=51),
            end=survey_schedule.start + relativedelta(days=100),
            full_enrollment_datetime=survey_schedule.start + relativedelta(days=80))
        survey_schedule.add_survey(survey1, survey2)
        self.assertEqual([survey1], survey_schedule.get_surveys(
            reference_datetime=survey_schedule.start + relativedelta(days=2)))

    def test_get_survey_by_reference_datetime2(self):
        survey_schedule = self.make_survey_schedule()
        survey1 = Survey(
            map_area='test_community',
            start=survey_schedule.start + relativedelta(days=1),
            end=survey_schedule.start + relativedelta(days=50),
            full_enrollment_datetime=survey_schedule.start + relativedelta(days=30))
        survey2 = Survey(
            map_area='test_community',
            start=survey_schedule.start + relativedelta(days=51),
            end=survey_schedule.start + relativedelta(days=100),
            full_enrollment_datetime=survey_schedule.start + relativedelta(days=80))
        survey_schedule.add_survey(survey1, survey2)
        self.assertEqual([survey2], survey_schedule.get_surveys(
            reference_datetime=survey_schedule.start + relativedelta(days=80)))
