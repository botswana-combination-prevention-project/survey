import sys

from dateutil.relativedelta import relativedelta

from django.core.management.color import color_style

from ..site_surveys import site_surveys


class DatesTestMixin:

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        style = color_style()
        sys.stdout.write(
            style.ERROR('{}. Overwriting survey dates.\n'.format(
                cls.__name__)))
        if not site_surveys._backup_registry:
            site_surveys.backup_registry(clear=False)

            for survey_schedule in site_surveys.get_survey_schedules(
                    group_name='bcpp-survey'):

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
                group_name='bcpp-survey'):
            sys.stdout.write(' * {}: {} - {}\n'.format(
                survey_schedule.name,
                survey_schedule.start,
                survey_schedule.end))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
