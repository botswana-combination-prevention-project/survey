from django.test import TestCase

from .site_surveys import site_surveys
from survey.survey_schedule import SurveySchedule
from edc_base.utils import get_utcnow
from dateutil.relativedelta import relativedelta
from survey.exceptions import SurveyScheduleError, AlreadyRegistered, SurveyError
from survey.survey import Survey
from survey.test_mixins import SurveyMixin


class TestSurvey(SurveyMixin, TestCase):

    def test_schedule_good_dates(self):
        try:
            SurveySchedule(
                name='survey-1',
                start_date=(get_utcnow() - relativedelta(years=1)).date(),
                end_date=get_utcnow().date())
        except SurveyScheduleError:
            self.fail('SurveyScheduleError unexpectedly raised')

    def test_schedule_bad_dates(self):
        try:
            SurveySchedule(
                name='survey-1',
                start_date=get_utcnow().date(),
                end_date=(get_utcnow() - relativedelta(years=1)).date())
            self.fail('SurveyScheduleError unexpectedly NOT raised')
        except SurveyScheduleError:
            pass

    def test_schedule_bad_equal_dates(self):
        try:
            SurveySchedule(
                name='survey-1',
                start_date=get_utcnow().date(),
                end_date=get_utcnow().date())
            self.fail('SurveyScheduleError unexpectedly NOT raised')
        except SurveyScheduleError:
            pass

    def test_schedule_name_is_unique(self):
        survey_schedule = SurveySchedule(
            name='survey-2',
            start_date=(get_utcnow() - relativedelta(years=5)).date(),
            end_date=(get_utcnow() - relativedelta(years=4)).date())
        site_surveys.register(survey_schedule)
        self.assertRaises(AlreadyRegistered, site_surveys.register, survey_schedule)

    def test_create_survey(self):
        survey = Survey(
            map_area='test_community',
            start_date=(get_utcnow() - relativedelta(years=1)).date(),
            end_date=get_utcnow().date(),
            full_enrollment_date=(get_utcnow() - relativedelta(weeks=1)).date()
        )

    def test_create_survey_with_end_precedes_start_date(self):
        """Assert start date precedes end date."""
        self.assertRaises(
            SurveyError, Survey,
            map_area='test_community',
            start_date=get_utcnow().date(),
            end_date=(get_utcnow() - relativedelta(years=1)).date(),
            full_enrollment_date=(get_utcnow() - relativedelta(weeks=1)).date()
        )

    def test_create_survey_with_bad_start_equals_end_date(self):
        """Assert start date not equal to end date."""
        self.assertRaises(
            SurveyError, Survey,
            map_area='test_community',
            start_date=get_utcnow().date(),
            end_date=get_utcnow().date(),
            full_enrollment_date=(get_utcnow() - relativedelta(weeks=1)).date()
        )

    def test_create_survey_with_bad_enrollment_date(self):
        self.assertRaises(
            SurveyError, Survey,
            map_area='test_community',
            start_date=(get_utcnow() - relativedelta(years=2)).date(),
            end_date=(get_utcnow() - relativedelta(years=1)).date(),
            full_enrollment_date=get_utcnow().date()
        )

    def test_add_survey_to_schedule(self):
        survey_schedule = self.make_survey_schedule()
        survey = Survey(
            map_area='test_community',
            start_date=(get_utcnow() - relativedelta(years=4)).date(),
            end_date=(get_utcnow() - relativedelta(years=2)).date(),
            full_enrollment_date=(get_utcnow() - relativedelta(years=3)).date()
        )
        survey_schedule.add_survey(survey)

    def test_add_survey_with_bad_dates(self):
        survey_schedule = self.make_survey_schedule()
        bad_start_date = survey_schedule.start_date - relativedelta(years=1)
        end_date = survey_schedule.end_date
        survey = Survey(
            map_area='test_community',
            start_date=bad_start_date,
            end_date=end_date,
            full_enrollment_date=end_date - relativedelta(weeks=1)
        )
        self.assertRaises(SurveyScheduleError, survey_schedule.add_survey, survey)

    def test_add_survey_with_bad_dates2(self):
        survey_schedule = self.make_survey_schedule()
        start_date = survey_schedule.start_date
        bad_end_date = survey_schedule.end_date + relativedelta(years=1)
        survey = Survey(
            map_area='test_community',
            start_date=start_date,
            end_date=bad_end_date,
            full_enrollment_date=start_date + relativedelta(weeks=1)
        )
        self.assertRaises(SurveyScheduleError, survey_schedule.add_survey, survey)
