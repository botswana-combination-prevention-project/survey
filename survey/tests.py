# coding=utf-8

from dateutil.relativedelta import relativedelta

from django.test import TestCase, tag

from edc_base.utils import get_utcnow

from .exceptions import SurveyScheduleError, AlreadyRegistered, SurveyError
from .site_surveys import site_surveys
from .survey import Survey
from .survey_schedule import SurveySchedule
from .test_mixins import SurveyMixin
from survey.exceptions import AddSurveyMapAreaError, AddSurveyDateError, AddSurveyOverlapError
from survey.surveys import survey_one, survey_two, survey_three


class TestSurvey(SurveyMixin, TestCase):

    def setUp(self):
        site_surveys.clear_registry()

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

    def test_survey_schedule_name_is_unique(self):
        for n in range(1, 4):
            survey_schedule = SurveySchedule(
                name='survey-10',
                group_name='ESS',
                start_date=(get_utcnow() - relativedelta(years=5 + n)).date(),
                end_date=(get_utcnow() - relativedelta(years=4 + n)).date())
            if n == 1:
                site_surveys.register(survey_schedule)
            else:
                self.assertRaises(AlreadyRegistered, site_surveys.register, survey_schedule)

    def test_survey_schedule_date_is_unique(self):
        survey_schedule = SurveySchedule(
            name='survey-10',
            start_date=(get_utcnow() - relativedelta(years=5)).date(),
            end_date=(get_utcnow() - relativedelta(years=4)).date())
        site_surveys.register(survey_schedule)
        self.assertRaises(AlreadyRegistered, site_surveys.register, survey_schedule)

    def test_get_survey_schedules_by_group_name(self):
        schedules = []
        for n in range(1, 4):
            survey_schedule = SurveySchedule(
                name='survey-1{}'.format(n),
                group_name='ESS',
                start_date=(get_utcnow() - relativedelta(years=5 + n)).date(),
                end_date=(get_utcnow() - relativedelta(years=4 + n)).date())
            schedules.append(survey_schedule)
            site_surveys.register(survey_schedule)
        schedules.sort(key=lambda o: o.start_date)
        self.assertEqual(len(schedules), 3)
        self.assertEqual(site_surveys.get_survey_schedules('ESS'), schedules)

    def test_create_survey(self):
        try:
            Survey(
                map_area='test_community',
                start_date=(get_utcnow() - relativedelta(years=1)).date(),
                end_date=get_utcnow().date(),
                full_enrollment_date=(get_utcnow() - relativedelta(weeks=1)).date())
        except SurveyError:
            self.fail('SurveyError unexpectedly raised')

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
        self.assertRaises(AddSurveyDateError, survey_schedule.add_survey, survey)

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
        self.assertRaises(AddSurveyDateError, survey_schedule.add_survey, survey)

    def test_create_survey_with_map_areas(self):
        survey_schedule = self.make_survey_schedule(map_areas=['test_community'])
        self.assertEqual(survey_schedule.map_areas, ['test_community'])

    def test_survey_with_bad_map_area(self):
        survey_schedule = self.make_survey_schedule(map_areas=['test_community'])
        survey = Survey(
            map_area='blahblah',
            start_date=survey_schedule.start_date + relativedelta(days=1),
            end_date=survey_schedule.end_date - relativedelta(days=1),
            full_enrollment_date=survey_schedule.end_date - relativedelta(days=2))
        self.assertRaises(AddSurveyMapAreaError, survey_schedule.add_survey, survey)

    def test_survey_without_map_areas_accepts_any_map_area(self):
        survey_schedule = self.make_survey_schedule(map_areas=None)
        survey = Survey(
            map_area='blahblah',
            start_date=survey_schedule.start_date + relativedelta(days=1),
            end_date=survey_schedule.end_date - relativedelta(days=1),
            full_enrollment_date=survey_schedule.end_date - relativedelta(days=2))
        try:
            survey_schedule.add_survey(survey)
        except AddSurveyMapAreaError:
            self.fail('AddSurveyMapAreaError unexpectedly raised')

    def test_get_survey_by_map_area(self):
        survey_schedule = self.make_survey_schedule()
        survey = Survey(
            map_area='test_community',
            start_date=survey_schedule.start_date + relativedelta(days=1),
            end_date=survey_schedule.end_date - relativedelta(days=1),
            full_enrollment_date=survey_schedule.end_date - relativedelta(days=2))
        survey_schedule.add_survey(survey)
        self.assertEqual([survey], survey_schedule.get_surveys(map_area='test_community'))

    def test_get_survey_by_reference_date(self):
        survey_schedule = self.make_survey_schedule()
        survey1 = Survey(
            map_area='test_community',
            start_date=survey_schedule.start_date + relativedelta(days=1),
            end_date=survey_schedule.start_date + relativedelta(days=50),
            full_enrollment_date=survey_schedule.start_date + relativedelta(days=30))
        survey2 = Survey(
            map_area='test_community',
            start_date=survey_schedule.start_date + relativedelta(days=51),
            end_date=survey_schedule.start_date + relativedelta(days=100),
            full_enrollment_date=survey_schedule.start_date + relativedelta(days=80))
        survey_schedule.add_survey(survey1, survey2)
        self.assertEqual([survey1], survey_schedule.get_surveys(
            reference_date=survey_schedule.start_date + relativedelta(days=2)))

    def test_get_survey_by_reference_date2(self):
        survey_schedule = self.make_survey_schedule()
        survey1 = Survey(
            map_area='test_community',
            start_date=survey_schedule.start_date + relativedelta(days=1),
            end_date=survey_schedule.start_date + relativedelta(days=50),
            full_enrollment_date=survey_schedule.start_date + relativedelta(days=30))
        survey2 = Survey(
            map_area='test_community',
            start_date=survey_schedule.start_date + relativedelta(days=51),
            end_date=survey_schedule.start_date + relativedelta(days=100),
            full_enrollment_date=survey_schedule.start_date + relativedelta(days=80))
        survey_schedule.add_survey(survey1, survey2)
        self.assertEqual([survey2], survey_schedule.get_surveys(
            reference_date=survey_schedule.start_date + relativedelta(days=80)))

    def test_surveys_in_map_area_cannot_overlap(self):
        survey_schedule = self.make_survey_schedule()
        survey1 = Survey(
            map_area='test_community',
            start_date=survey_schedule.start_date + relativedelta(days=1),
            end_date=survey_schedule.start_date + relativedelta(days=50),
            full_enrollment_date=survey_schedule.start_date + relativedelta(days=30))
        survey2 = Survey(
            map_area='test_community',
            start_date=survey_schedule.start_date + relativedelta(days=30),
            end_date=survey_schedule.start_date + relativedelta(days=100),
            full_enrollment_date=survey_schedule.start_date + relativedelta(days=80))
        self.assertRaises(AddSurveyOverlapError, survey_schedule.add_survey, survey1, survey2)

    def test_get_current_survey(self):
        site_surveys.register(survey_one)
        site_surveys.register(survey_two)
        site_surveys.register(survey_three)
        survey = site_surveys.get_survey('year-1.annual.test_community')
        try:
            self.assertEqual(survey.label, 'annual.test_community')
        except AttributeError:
            self.fail('annual.test_community unexpectedly does not exist. Got {}'.format(survey))
