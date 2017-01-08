# coding=utf-8

from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_base.utils import get_utcnow

from .exceptions import SurveyScheduleError, AlreadyRegistered, SurveyError
from .site_surveys import site_surveys
from .survey import Survey
from .survey_schedule import SurveySchedule
from .test_mixins import SurveyMixin
from .apps import S
from survey.exceptions import AddSurveyMapAreaError, AddSurveyDateError, AddSurveyOverlapError
from survey.surveys import survey_one, survey_two, survey_three


class TestSurvey(SurveyMixin, TestCase):

    def setUp(self):
        site_surveys.clear_registry()

    def test_schedule_good_dates(self):
        try:
            SurveySchedule(
                name='survey-1',
                start=(get_utcnow() - relativedelta(years=1)),
                end=get_utcnow())
        except SurveyScheduleError:
            self.fail('SurveyScheduleError unexpectedly raised')

    def test_schedule_bad_dates(self):
        try:
            SurveySchedule(
                name='survey-1',
                start=get_utcnow(),
                end=(get_utcnow() - relativedelta(years=1)))
            self.fail('SurveyScheduleError unexpectedly NOT raised')
        except SurveyScheduleError:
            pass

    def test_survey_schedule_name_is_unique(self):
        for n in range(1, 4):
            survey_schedule = SurveySchedule(
                name='survey-10',
                group_name='ESS',
                start=(get_utcnow() - relativedelta(years=5 + n)),
                end=(get_utcnow() - relativedelta(years=4 + n)))
            if n == 1:
                site_surveys.register(survey_schedule)
            else:
                self.assertRaises(AlreadyRegistered, site_surveys.register, survey_schedule)

    def test_survey_schedule_date_is_unique(self):
        survey_schedule = SurveySchedule(
            name='survey-10',
            start=(get_utcnow() - relativedelta(years=5)),
            end=(get_utcnow() - relativedelta(years=4)))
        site_surveys.register(survey_schedule)
        self.assertRaises(AlreadyRegistered, site_surveys.register, survey_schedule)

    def test_get_survey_schedules_by_group_name(self):
        schedules = []
        for n in range(1, 4):
            survey_schedule = SurveySchedule(
                name='survey-1{}'.format(n),
                group_name='ESS',
                start=(get_utcnow() - relativedelta(years=5 + n)),
                end=(get_utcnow() - relativedelta(years=4 + n)))
            schedules.append(survey_schedule)
            site_surveys.register(survey_schedule)
        schedules.sort(key=lambda o: o.start)
        self.assertEqual(len(schedules), 3)
        self.assertEqual(site_surveys.get_survey_schedules('ESS'), schedules)

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
            SurveyError, Survey,
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
        self.assertRaises(AddSurveyDateError, survey_schedule.add_survey, survey)

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
        self.assertRaises(AddSurveyDateError, survey_schedule.add_survey, survey)

    def test_create_survey_with_map_areas(self):
        survey_schedule = self.make_survey_schedule(map_areas=['test_community'])
        self.assertEqual(survey_schedule.map_areas, ['test_community'])

    def test_survey_with_bad_map_area(self):
        survey_schedule = self.make_survey_schedule(map_areas=['test_community'])
        survey = Survey(
            map_area='blahblah',
            start=survey_schedule.start + relativedelta(days=1),
            end=survey_schedule.end - relativedelta(days=1),
            full_enrollment_datetime=survey_schedule.end - relativedelta(days=2))
        self.assertRaises(AddSurveyMapAreaError, survey_schedule.add_survey, survey)

    def test_survey_without_map_areas_accepts_any_map_area(self):
        survey_schedule = self.make_survey_schedule(map_areas=None)
        survey = Survey(
            map_area='blahblah',
            start=survey_schedule.start + relativedelta(days=1),
            end=survey_schedule.end - relativedelta(days=1),
            full_enrollment_datetime=survey_schedule.end - relativedelta(days=2))
        try:
            survey_schedule.add_survey(survey)
        except AddSurveyMapAreaError:
            self.fail('AddSurveyMapAreaError unexpectedly raised')

    def test_get_survey_by_map_area(self):
        survey_schedule = self.make_survey_schedule()
        survey = Survey(
            map_area='test_community',
            start=survey_schedule.start + relativedelta(days=1),
            end=survey_schedule.end - relativedelta(days=1),
            full_enrollment_datetime=survey_schedule.end - relativedelta(days=2))
        survey_schedule.add_survey(survey)
        self.assertEqual([survey], survey_schedule.get_surveys(map_area='test_community'))

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


class TestSurveyOrder(SurveyMixin, TestCase):

    def setUp(self):
        site_surveys.clear_registry()
        self.survey_schedule = self.make_survey_schedule(name='year-1')
        self.survey1 = Survey(
            name='survey1',
            map_area='test_community',
            start=self.survey_schedule.start + relativedelta(days=1),
            end=self.survey_schedule.start + relativedelta(days=50),
            full_enrollment_datetime=self.survey_schedule.start + relativedelta(days=30))
        self.survey2 = Survey(
            name='survey2',
            map_area='test_community',
            start=self.survey_schedule.start + relativedelta(days=51),
            end=self.survey_schedule.start + relativedelta(days=100),
            full_enrollment_datetime=self.survey_schedule.start + relativedelta(days=80))
        self.survey3 = Survey(
            name='survey3',
            map_area='test_community',
            start=self.survey_schedule.start + relativedelta(days=101),
            end=self.survey_schedule.start + relativedelta(days=150),
            full_enrollment_datetime=self.survey_schedule.start + relativedelta(days=120))
        self.current_surveys = [
            S('test_survey.year-1.survey1.test_community'),
            S('test_survey.year-1.survey2.test_community'),
            S('test_survey.year-1.survey3.test_community')]

    def tearDown(self):
        site_surveys.restore_registry()
        super().tearDown()

    def test_surveys_always_ordered(self):
        self.survey_schedule.add_survey(self.survey3, self.survey1, self.survey2)
        surveys = self.survey_schedule.surveys
        self.assertEqual(surveys[0], self.survey1)
        self.assertEqual(surveys[1], self.survey2)
        self.assertEqual(surveys[2], self.survey3)

    def test_get_previous_survey(self):
        self.survey_schedule.add_survey(self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_surveys)
        surveys = site_surveys.surveys
        self.assertEqual(surveys[0].previous, None)
        self.assertEqual(surveys[1].previous, self.survey1)
        self.assertEqual(surveys[2].previous, self.survey2)

    def test_get_next_survey(self):
        self.survey_schedule.add_survey(self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_surveys)
        surveys = site_surveys.surveys
        self.assertEqual(surveys[0].next, self.survey2)
        self.assertEqual(surveys[1].next, self.survey3)
        self.assertEqual(surveys[2].next, None)

    def test_register_current(self):
        self.survey_schedule.add_survey(self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_surveys)
        self.assertEqual(len(site_surveys.current_surveys), 3)

    def test_current_has_flag_set(self):
        """Asserts survey instance is set, from current surveys."""
        self.survey_schedule.add_survey(self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_surveys)
        for survey in site_surveys.current_surveys:
            self.assertTrue(survey.current)

    def test_current_has_flag_set2(self):
        """Asserts survey instance is set, in the surveys register."""
        self.survey_schedule.add_survey(self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_surveys)
        for survey in site_surveys.surveys:
            if survey.field_value in [survey.field_value for survey in site_surveys.current_surveys]:
                self.assertTrue(survey.current)
