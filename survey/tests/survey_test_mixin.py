from dateutil.relativedelta import relativedelta
from faker import Faker

from edc_base.utils import get_utcnow
from edc_base_test.exceptions import TestMixinError

from ..site_surveys import site_surveys
from ..survey_schedule import SurveySchedule

fake = Faker()


class SurveyTestMixin:

    def setUp(self):
        super().setUp()
        # site_surveys.backup_registry(clear=False)

    def tearDown(self):
        super().tearDown()
        #site_surveys.restore_registry()

    def make_survey_schedule(self, group_name=None, name=None, **options):
        return SurveySchedule(
            name=name or fake.safe_color_name(),
            group_name=group_name or 'test_survey',
            start=(get_utcnow() - relativedelta(years=5)),
            end=(get_utcnow() - relativedelta(years=1)),
            **options)

    def is_survey_schedule(self, survey_schedule):
        """Verifies the survey schedule object is valid.

        Does not have to be a current survey schedule."""
        if survey_schedule:
            survey_schedule = site_surveys.get_survey_schedule_from_field_value(
                survey_schedule.field_value)
            if not survey_schedule:
                raise TestMixinError(
                    'Invalid survey specified. Got {}. See TestCase {} '
                    'Expected one of {}'.format(
                        survey_schedule.field_value,
                        self.__class__.__name__,
                        [s.field_value for s in site_surveys.get_survey_schedules()]))
        return survey_schedule

    def get_survey_schedule(self, name=None, index=None, field_value=None,
                            group_name=None, current=None):
        """Returns a survey schedule object.

        You can also just use site_surveys!

            * name: survey schedule name, e.g. 'bcpp_year.example-year-1'
            * field_value: survey schedule field_value, e.g. 'bcpp_year.example-year-1.test_community'
            * group_name: survey schedule group_name, e.g. 'bcpp_year'.
            * index: list index of the ordered list of survey schedules
            * current: if current=True only return a survey schedule if it is a current.
                       If group_name is None, current defaults to True"""
        if name:
            survey_schedule = site_surveys.get_survey_schedule(name=name)
            if current:
                survey_schedule = survey_schedule if survey_schedule.current else None
        else:
            current = current if group_name else True
            survey_schedules = site_surveys.get_survey_schedules(
                group_name=group_name, current=current)
            survey_schedule = survey_schedules[index or 0]
        return survey_schedule
