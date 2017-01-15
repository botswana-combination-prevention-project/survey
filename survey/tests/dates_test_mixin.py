import copy
import sys

from dateutil.relativedelta import relativedelta
from faker import Faker

from django.apps import apps as django_apps
from django.core.management.color import color_style

from edc_base_test.mixins.dates_test_mixin import DatesTestMixin as DatesTestMixinParent

from survey.site_surveys import site_surveys
from pprint import pprint


fake = Faker()


class DatesTestMixin(DatesTestMixinParent):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        style = color_style()
        sys.stdout.write(
            style.NOTICE(
                '\n{}. Overwriting survey schedule and survey start/end dates '
                'for tests only.\n'.format(cls.__name__)))
        cls.prepare_site_surveys_for_tests()

    @classmethod
    def tearDownClass(cls):
        """Restores edc_protocol app_config open/close dates and edc_consent site_consents registry."""
        super().tearDownClass()
        site_surveys.autodiscover()
        site_surveys.restore_registry()
    
    @classmethod
    def prepare_site_surveys_for_tests(cls):
        style = color_style()
        edc_protocol_app_config = django_apps.get_app_config('edc_protocol')

        tdelta = (site_surveys.get_survey_schedules()[0].rstart.floor('hour').datetime -
                  edc_protocol_app_config.arrow.ropen.floor('hour').datetime)

        test_survey_schedules = []
        testsurveys = []
        for survey_schedule in site_surveys.get_survey_schedules():

            if survey_schedule.surveys:
                tdelta_survey = (survey_schedule.surveys[0].rstart.floor('hour').datetime -
                                 edc_protocol_app_config.arrow.ropen.floor('hour').datetime)
                for survey in survey_schedule.surveys:
                    test_survey = copy.copy(survey)
                    test_survey.start = (
                        test_survey.rstart.floor('hour').datetime - relativedelta(days=tdelta_survey.days))
                    test_survey.end = (
                        test_survey.rend.ceil('hour').datetime - relativedelta(days=tdelta_survey.days))
                    testsurveys.append(test_survey)

            test_survey_schedule = copy.copy(survey_schedule)
            test_survey_schedule.start = (
                test_survey_schedule.rstart.floor('hour').datetime - relativedelta(days=tdelta.days))
            test_survey_schedule.end = (
                test_survey_schedule.rend.ceil('hour').datetime - relativedelta(days=tdelta.days))

            test_survey_schedule.registry = testsurveys

            sys.stdout.write(style.NOTICE(
                ' * {}: {} - {}\n'.format(test_survey_schedule.name, test_survey_schedule.start, test_survey_schedule.end)))

            test_survey_schedules.append(test_survey_schedule)

        site_surveys.backup_registry(clear=True)
        for test_survey_schedule in test_survey_schedules:
            site_surveys.register(test_survey_schedule)
