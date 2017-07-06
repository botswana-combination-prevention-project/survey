import sys

from dateutil.relativedelta import relativedelta

from django.core.management.color import color_style

from .load_test_surveys import site_surveys


class DatesTestMixin:

    site_survey_group_name = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        style = color_style()
        sys.stdout.write(
            style.ERROR(f'{cls.__name__}. Overwriting survey dates.\n'))
        for survey_schedule in site_surveys.get_survey_schedules(
                group_name=cls.site_survey_group_name):
            for survey in survey_schedule.surveys:
                survey.start = survey.start - relativedelta(
                    days=cls.study_tdelta.days)
                survey.end = survey.end - relativedelta(
                    days=cls.study_tdelta.days)

            survey_schedule.start = (
                survey_schedule.start - relativedelta(
                    days=cls.study_tdelta.days))
            survey_schedule.end = (
                survey_schedule.end - relativedelta(
                    days=cls.study_tdelta.days))

        for survey_schedule in site_surveys.get_survey_schedules(
                group_name=cls.site_survey_group_name):
            sys.stdout.write(
                f' * {survey_schedule.name}: {survey_schedule.start} - '
                f'{survey_schedule.end}\n')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
