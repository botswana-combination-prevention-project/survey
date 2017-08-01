from django.test import TestCase, tag
from dateutil.relativedelta import relativedelta
from edc_base.utils import get_utcnow

from ..helpers import CurrentSurveyError
from ..site_surveys import SiteSurveys, SiteSurveysRegistryNotLoaded
from ..site_surveys import site_surveys, SiteSurveysAlreadyRegistered
from ..site_surveys import SiteSurveysError
from ..site_surveys import CurrentSurveySchedulesAlreadyLoaded
from ..sparser import S
from ..survey import Survey
from ..survey_schedule import SurveySchedule
from .survey_test_helper import SurveyTestHelper
from .surveys import survey_one, survey_three, survey_two
from copy import copy
from pprint import pprint


class DummySurveySchedule:
    def __init__(self, name=None, surveys=None, group_name=None):
        self.surveys = surveys or [1, 2, 3]
        self.name = name or 'erik'
        self.group_name = group_name or 'erik'
        self.start = get_utcnow()


@tag('site_surveys')
class TestSiteSurvey(TestCase):

    def test_repr(self):
        self.assertTrue(repr(site_surveys))

    def test_str(self):
        self.assertTrue(str(site_surveys))


@tag('site_surveys')
class TestSiteSurveyRegisterCurrent(TestCase):

    """Assertions for registering the current survey schedules as done
    through AppConfig using site_survey.register_current().

    Flagging a survey schedule as "current" is only valid if the schedule
    is already registered using site_survey.register().
    """

    def setUp(self):
        site_surveys._registry = []
        site_surveys.loaded = False
        site_surveys.loaded_current = False

    def test_site_survey_registry_register_current_ok(self):
        site_surveys.register(survey_one)
        sparser = S('test_survey.year-1.baseline.test_community')
        try:
            site_surveys.register_current(sparser)
        except SiteSurveysRegistryNotLoaded as e:
            self.fail(
                f'SiteSurveysRegistryNotLoaded unexpectedly raised. Got {e}')

    def test_site_survey_registry_register_current_raises(self):
        sparser = S('test_survey.year-1.baseline.test_community')
        self.assertRaises(
            SiteSurveysRegistryNotLoaded,
            site_surveys.register_current, sparser)

    def test_site_survey_registry_register_current_bad_survey_schedule(self):
        site_surveys.register(survey_one)
        sparser = S('test_survey.year-2.baseline.test_community')
        self.assertRaises(
            CurrentSurveyError,
            site_surveys.register_current, sparser)

    def test_site_survey_registry_register_current_bad_survey(self):
        site_surveys.register(survey_one)
        sparser = S('test_survey.year-1.blahblah.test_community')
        with self.assertRaises(CurrentSurveyError) as cm:
            site_surveys.register_current(sparser)
        self.assertEqual(cm.exception.code, 'survey_name')

    def test_site_survey_registry_register_current_bad_group_name(self):
        site_surveys.register(survey_one)
        sparser = S('blah_group.year-1.baseline.test_community')
        with self.assertRaises(CurrentSurveyError) as cm:
            site_surveys.register_current(sparser)
        self.assertEqual(cm.exception.code, 'not_found')


@tag('site_surveys')
class TestSiteSurveyRegister(TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        site_surveys._registry = []
        site_surveys.loaded = False
        site_surveys.loaded_current = False

    def test_site_survey_registry_register_no_surveys_raises(self):
        dummy = DummySurveySchedule()
        dummy.surveys = None
        test_site_surveys = SiteSurveys()
        self.assertRaises(
            SiteSurveysError,
            test_site_surveys.register, dummy)

    def test_site_survey_registry_raises_already_registered(self):
        dummy = DummySurveySchedule()
        site_surveys.register(dummy)
        self.assertRaises(
            SiteSurveysAlreadyRegistered,
            site_surveys.register, dummy)

    def test_site_survey_registry_register_current_raises_not_loaded(self):
        self.assertRaises(
            SiteSurveysRegistryNotLoaded,
            site_surveys.register_current, DummySurveySchedule())

    def test_site_survey_registry_raises_not_loaded(self):
        """Asserts any access to the registry raises not loaded.
        """
        self.assertRaises(
            SiteSurveysRegistryNotLoaded,
            site_surveys.get_survey_schedules)

    def test_site_survey_registry_register_current_ok(self):
        site_surveys = SiteSurveys()
        site_surveys.register(survey_one)
        site_surveys.register_current(survey_one)


@tag('site_surveys')
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
        self.survey_helper.load_test_surveys(register_current=False)
        survey_blah = SurveySchedule(
            name='year-1',
            group_name='blahblahblah',
            map_area='test_community',
            start=(get_utcnow() - relativedelta(years=3)),
            end=(get_utcnow() - relativedelta(years=2)))
        survey_blah.add_survey(copy(survey_one.surveys[0]))
        with self.assertRaises(CurrentSurveyError) as cm:
            site_surveys.register_current(survey_blah)
        self.assertEqual(cm.exception.code, 'not_found')

    def test_current_survey_schedules_already_loaded(self):
        self.assertRaises(
            CurrentSurveySchedulesAlreadyLoaded,
            site_surveys.register_current, survey_two)

    def test_site_survey_already_registered_name(self):
        survey_schedule = SurveySchedule(
            name='survey',
            group_name='ESS',
            start=(get_utcnow() - relativedelta(years=1)),
            end=(get_utcnow()))
        survey_schedule.registry = ['fake_survey']
        site_surveys.register(survey_schedule)
        self.assertRaises(
            SiteSurveysAlreadyRegistered,
            site_surveys.register, survey_schedule)

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

    def test_survey_schedule_date_is_unique(self):
        survey_schedule = SurveySchedule(
            name='survey-10',
            start=(get_utcnow() - relativedelta(years=5)),
            end=(get_utcnow() - relativedelta(years=4)))
        survey_schedule.registry = ['fake_survey']
        site_surveys.register(survey_schedule)
        self.assertRaises(
            SiteSurveysAlreadyRegistered, site_surveys.register, survey_schedule)

    def test_get_survey_schedules_by_group_name(self):
        self.assertEqual(
            site_surveys.get_survey_schedules('test_survey'), [survey_one])


@tag('site_surveys')
class TestSiteSurveys2(TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()

    def test_get_survey_by_field_value(self):
        survey_schedule = site_surveys.get_survey_schedule(
            survey_one.short_name)
        survey = survey_schedule.surveys[1]
        self.assertIsNotNone(survey.field_value)
        self.assertEqual(
            survey.field_value,
            site_surveys.get_survey_from_field_value(survey.field_value).field_value)

    def test_get_survey_schedule_by_field_value(self):
        survey_schedule = site_surveys.get_survey_schedule(
            survey_one.short_name)
        survey_schedule = site_surveys.get_survey_schedule_from_field_value(
            survey_schedule.field_value)
        self.assertEqual(
            survey_schedule.field_value,
            site_surveys.get_survey_schedule_from_field_value(
                survey_schedule.field_value).field_value)

    def test_get_survey_schedule_by_field_value_none(self):
        self.assertIsNone(
            site_surveys.get_survey_from_field_value(None))

    def test_get_survey_schedule_bad_field_value(self):
        self.assertRaises(
            SiteSurveysError,
            site_surveys.get_survey_schedule_from_field_value,
            'test_survey.blahblah')

    def test_get_survey(self):
        self.survey_helper.load_test_surveys(load_all=True)
        self.assertEqual(
            'test_survey.year-2.baseline.test_community',
            site_surveys.get_survey(
                'test_survey.year-2.baseline.test_community').field_value)

    def test_get_survey_current(self):
        self.survey_helper.load_test_surveys(
            load_all=True,
            current_survey_index=1)
        self.assertEqual(
            'test_survey.year-2.baseline.test_community',
            site_surveys.get_survey(
                'test_survey.year-2.baseline.test_community',
                current=True).field_value)

    def test_get_survey_current_none(self):
        self.survey_helper.load_test_surveys(
            load_all=True,
            current_survey_index=1)
        self.assertIsNone(
            site_surveys.get_survey(
                'test_survey.year-1.baseline.test_community',
                current=True))

    def test_get_survey_names(self):
        self.survey_helper.load_test_surveys()
        self.assertEqual(
            site_surveys.get_survey_names(),
            [s.field_value for s in survey_one.surveys])

    def test_get_survey_names_group(self):
        self.survey_helper.load_test_surveys()
        self.assertEqual(
            site_surveys.get_survey_names('test_survey'),
            [s.field_value for s in survey_one.surveys])

    def test_get_survey_schedule_field_values(self):
        self.survey_helper.load_test_surveys(load_all=True)
        self.assertEqual(
            site_surveys.get_survey_schedule_field_values(),
            [survey_one.field_value, survey_two.field_value, survey_three.field_value])

    def test_get_map_areas(self):
        self.survey_helper.load_test_surveys(load_all=True)
        self.assertEqual(site_surveys.map_areas, ['test_community'])

    def test_get_current_map_areas_none(self):
        self.survey_helper.load_test_surveys(
            load_all=True, register_current=False)
        self.assertEqual(site_surveys.current_map_areas, [])

    def test_get_current_map_areas(self):
        self.survey_helper.load_test_surveys(
            load_all=True, register_current=True)
        self.assertEqual(site_surveys.current_map_areas, ['test_community'])


@tag('site_surveys')
class TestSiteSurveysSurveyOrder(TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        site_surveys._registry = []
        site_surveys.loaded = False
        site_surveys.loaded_current = False

        self.survey_schedule = self.survey_helper.make_survey_schedule(
            name='year-1')
        self.survey1 = Survey(
            position=0,
            name='survey1',
            map_area='test_community',
            start=self.survey_schedule.start + relativedelta(days=1),
            end=self.survey_schedule.start + relativedelta(days=50),
            full_enrollment_datetime=(self.survey_schedule.start
                                      + relativedelta(days=30)))
        self.survey2 = Survey(
            position=1,
            name='survey2',
            map_area='test_community',
            start=self.survey_schedule.start + relativedelta(days=51),
            end=self.survey_schedule.start + relativedelta(days=100),
            full_enrollment_datetime=(self.survey_schedule.start
                                      + relativedelta(days=80)))
        self.survey3 = Survey(
            position=3,
            name='survey3',
            map_area='test_community',
            start=self.survey_schedule.start + relativedelta(days=101),
            end=self.survey_schedule.start + relativedelta(days=150),
            full_enrollment_datetime=(self.survey_schedule.start
                                      + relativedelta(days=120)))
        self.current_sparsers = [
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
        site_surveys.register_current(*self.current_sparsers)
        surveys = site_surveys.surveys
        self.assertEqual(surveys[0].previous, None)
        self.assertEqual(surveys[1].previous, self.survey1)
        self.assertEqual(surveys[2].previous, self.survey2)

    def test_get_next_survey(self):
        self.survey_schedule.add_survey(
            self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_sparsers)
        surveys = site_surveys.surveys
        self.assertEqual(surveys[0].next, self.survey2)
        self.assertEqual(surveys[1].next, self.survey3)
        self.assertEqual(surveys[2].next, None)

    def test_register_current(self):
        self.survey_schedule.add_survey(
            self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_sparsers)
        self.assertEqual(len(site_surveys.current_surveys), 3)

    def test_current_has_flag_set(self):
        """Asserts survey instance is set, from current surveys.
        """
        self.survey_schedule.add_survey(
            self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_sparsers)
        for survey in site_surveys.current_surveys:
            self.assertTrue(survey.current)

    def test_current_has_flag_set2(self):
        """Asserts survey instance is set, in the surveys register.
        """
        self.survey_schedule.add_survey(
            self.survey3, self.survey1, self.survey2)
        site_surveys.register(self.survey_schedule)
        site_surveys.register_current(*self.current_sparsers)
        for survey in site_surveys.surveys:
            if survey.field_value in [
                    survey.field_value for survey in site_surveys.current_surveys]:
                self.assertTrue(survey.current)
