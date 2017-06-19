from django.apps import apps as django_apps
from django.test import TestCase, tag
from dateutil.relativedelta import relativedelta
from edc_base.utils import get_utcnow

from ..site_surveys import SiteSurveys, SiteSurveysRegistryNotLoaded
from ..site_surveys import SiteSurveysAlreadyRegistered
from ..site_surveys import site_surveys, SiteSurveysError
from ..sparser import S
from ..survey import Survey
from ..survey_schedule import SurveySchedule
from .survey_test_helper import SurveyTestHelper


class TestSiteSurveys(TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()

    def test_site_survey_registry(self):
        test_site_surveys = SiteSurveys()
        self.assertRaises(
            SiteSurveysRegistryNotLoaded,
            test_site_surveys.get_survey_schedules)

    def test_site_survey_registry_current1(self):
        """Asserts cannot register the current survey if registry
        not loaded.
        """
        test_site_surveys = SiteSurveys()
        self.assertRaises(
            SiteSurveysRegistryNotLoaded,
            test_site_surveys.register_current, 'blah')

    def test_site_survey_registry_current_group_name(self):
        """Asserts cannot register a current survey if that survey
        is not in the registry.
        """
        test_site_surveys = SiteSurveys()
        survey_schedule_blah = SurveySchedule(
            name='blah',
            group_name='BLAH',
            start=(get_utcnow() - relativedelta(years=1)),
            end=(get_utcnow()))
        survey_schedule_blah.registry = ['fake_survey']
        survey_schedule = SurveySchedule(
            name='survey',
            group_name='ESS',
            start=(get_utcnow() - relativedelta(years=1)),
            end=(get_utcnow()))
        survey_schedule.registry = ['fake_survey']
        test_site_surveys.register(survey_schedule)
        self.assertRaises(
            SiteSurveysError,
            test_site_surveys.register_current, survey_schedule_blah)

    def test_site_survey_registry_current_surveys(self):
        test_site_surveys = SiteSurveys()
        survey_schedule = SurveySchedule(
            name='year-1',
            group_name='bcpp',
            start=(get_utcnow() - relativedelta(years=1)),
            end=(get_utcnow()))
        survey1 = Survey(
            name='survey1',
            map_area='test_community',
            start=survey_schedule.start + relativedelta(days=1),
            end=survey_schedule.start + relativedelta(days=50),
            full_enrollment_datetime=(survey_schedule.start
                                      + relativedelta(days=30)))
        survey_schedule.add_survey(survey1)
        s1 = S('bcpp.year-1.survey1.test_community')
        s2 = S('bcpp.year-2.survey2.test_community')
        test_site_surveys.register(survey_schedule)
        test_site_surveys.register_current(s1)
        self.assertRaises(
            SiteSurveysError,
            test_site_surveys.register_current, s2)

    def test_site_survey_already_registered_name(self):
        test_site_surveys = SiteSurveys()
        survey_schedule = SurveySchedule(
            name='survey',
            group_name='ESS',
            start=(get_utcnow() - relativedelta(years=1)),
            end=(get_utcnow()))
        survey_schedule.registry = ['fake_survey']
        test_site_surveys.register(survey_schedule)
        self.assertRaises(
            SiteSurveysAlreadyRegistered,
            test_site_surveys.register, survey_schedule)

    def test_site_survey_already_registered_group(self):
        test_site_surveys = SiteSurveys()
        survey_schedule1 = SurveySchedule(
            name='survey1',
            group_name='ESS',
            start=(get_utcnow() - relativedelta(years=1)),
            end=(get_utcnow()))
        survey_schedule1.registry = ['fake_survey']
        survey_schedule2 = SurveySchedule(
            name='survey2',
            group_name='ESS',
            start=(get_utcnow() - relativedelta(years=1)),
            end=(get_utcnow()))
        survey_schedule2.registry = ['fake_survey']
        test_site_surveys.register(survey_schedule1)
        self.assertRaises(
            SiteSurveysAlreadyRegistered,
            test_site_surveys.register, survey_schedule2)

    def test_survey_schedule_name_is_unique(self):

        survey_schedules = []
        for n in range(1, 4):
            survey_schedule = SurveySchedule(
                name='survey-10',
                group_name='ESS',
                start=(get_utcnow() - relativedelta(years=5 + n)),
                end=(get_utcnow() - relativedelta(years=4 + n)))
            survey_schedule.registry = ['fake_survey']
            survey_schedules.append(survey_schedule)
            if n == 1:
                site_surveys.register(survey_schedule)
            else:
                self.assertRaises(
                    SiteSurveysAlreadyRegistered,
                    site_surveys.register, survey_schedule)
        for survey_schedule in survey_schedules:
            site_surveys.unregister(survey_schedule)

    def test_survey_schedule_date_is_unique(self):
        survey_schedule = SurveySchedule(
            name='survey-10',
            start=(get_utcnow() - relativedelta(years=5)),
            end=(get_utcnow() - relativedelta(years=4)))
        survey_schedule.registry = ['fake_survey']
        site_surveys.register(survey_schedule)
        self.assertRaises(
            SiteSurveysAlreadyRegistered, site_surveys.register, survey_schedule)
        site_surveys.unregister(survey_schedule)

    def test_get_survey_schedules_by_group_name(self):
        survey_schedules = []
        for n in range(1, 4):
            survey_schedule = SurveySchedule(
                name='survey-1{}'.format(n),
                group_name='ESS',
                start=(get_utcnow() - relativedelta(years=5 + n)),
                end=(get_utcnow() - relativedelta(years=4 + n)))
            survey_schedule.registry = ['fake_survey']
            survey_schedules.append(survey_schedule)
            site_surveys.register(survey_schedule)
        survey_schedules.sort(key=lambda o: o.start)
        self.assertEqual(len(survey_schedules), 3)
        self.assertEqual(
            site_surveys.get_survey_schedules('ESS'), survey_schedules)
        for survey_schedule in survey_schedules:
            site_surveys.unregister(survey_schedule)


class TestSiteSurveys2(TestCase):

    def test_get_survey_by_field_value(self):
        app_config = django_apps.get_app_config('survey')
        field_value = app_config.current_surveys[0].field_value
        self.assertIsNotNone(field_value)
        survey = site_surveys.get_survey_from_field_value(field_value)
        self.assertEqual(
            survey.field_value, field_value)

    def test_get_survey_schedule_by_field_value(self):
        app_config = django_apps.get_app_config('survey')
        field_value = app_config.current_surveys[0].field_value
        self.assertIsNotNone(field_value)
        s = S(field_value)
        survey_schedule = site_surveys.get_survey_schedule_from_field_value(
            field_value)
        self.assertEqual(
            survey_schedule.field_value, s.survey_schedule_field_value)


class TestSiteSurveysSurveyOrder(TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        site_surveys.backup_registry(clear=True)

        self.survey_schedule = self.survey_helper.make_survey_schedule(
            name='year-1')
        self.survey1 = Survey(
            name='survey1',
            map_area='test_community',
            start=self.survey_schedule.start + relativedelta(days=1),
            end=self.survey_schedule.start + relativedelta(days=50),
            full_enrollment_datetime=(self.survey_schedule.start
                                      + relativedelta(days=30)))
        self.survey2 = Survey(
            name='survey2',
            map_area='test_community',
            start=self.survey_schedule.start + relativedelta(days=51),
            end=self.survey_schedule.start + relativedelta(days=100),
            full_enrollment_datetime=(self.survey_schedule.start
                                      + relativedelta(days=80)))
        self.survey3 = Survey(
            name='survey3',
            map_area='test_community',
            start=self.survey_schedule.start + relativedelta(days=101),
            end=self.survey_schedule.start + relativedelta(days=150),
            full_enrollment_datetime=(self.survey_schedule.start
                                      + relativedelta(days=120)))
        self.current_surveys = [
            S('test_survey.year-1.survey1.test_community'),
            S('test_survey.year-1.survey2.test_community'),
            S('test_survey.year-1.survey3.test_community')]

    def test_surveys_always_ordered(self):
        self.survey_schedule.add_survey(
            self.survey3, self.survey1, self.survey2)
        surveys = self.survey_schedule.surveys
        self.assertEqual(surveys[0], self.survey1)
        self.assertEqual(surveys[1], self.survey2)
        self.assertEqual(surveys[2], self.survey3)

    def test_get_previous_survey(self):
        self.survey_schedule.add_survey(
            self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_surveys)
        surveys = site_surveys.surveys
        self.assertEqual(surveys[0].previous, None)
        self.assertEqual(surveys[1].previous, self.survey1)
        self.assertEqual(surveys[2].previous, self.survey2)

    def test_get_next_survey(self):
        self.survey_schedule.add_survey(
            self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_surveys)
        surveys = site_surveys.surveys
        self.assertEqual(surveys[0].next, self.survey2)
        self.assertEqual(surveys[1].next, self.survey3)
        self.assertEqual(surveys[2].next, None)

    def test_register_current(self):
        self.survey_schedule.add_survey(
            self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_surveys)
        self.assertEqual(len(site_surveys.current_surveys), 3)

    def test_current_has_flag_set(self):
        """Asserts survey instance is set, from current surveys.
        """
        self.survey_schedule.add_survey(
            self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_surveys)
        for survey in site_surveys.current_surveys:
            self.assertTrue(survey.current)

    def test_current_has_flag_set2(self):
        """Asserts survey instance is set, in the surveys register.
        """
        self.survey_schedule.add_survey(
            self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_surveys)
        for survey in site_surveys.surveys:
            if survey.field_value in [
                    survey.field_value for survey in site_surveys.current_surveys]:
                self.assertTrue(survey.current)
