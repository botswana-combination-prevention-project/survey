# coding=utf-8

import sys

from django.apps import AppConfig as DjangoApponfig
from django.conf import settings
from django.core.management.color import color_style

from .site_surveys import site_surveys
from survey.exceptions import SurveyError

style = color_style()


class AppConfig(DjangoApponfig):
    name = 'survey'
    active_survey_schedule_groups = ['test_survey']
    current_survey_label = 'annual.test_community'

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_surveys.autodiscover()
        try:
            self.current_survey_name = settings.CURRENT_SURVEY
        except AttributeError:
            pass
        for group_name in self.active_survey_schedule_groups:
            if not site_surveys.get_survey_schedules(group_name=group_name):
                raise SurveyError(
                    'Invalid group name. Got \'{}\'. Expected one of {}. See survey.apps.AppConfig'.format(
                        group_name, site_surveys.get_survey_schedule_group_names()))
        if not site_surveys.get_survey(self.current_survey_label):
            raise SurveyError(
                'Invalid current survey. Got \'{}\'. Expected one of {}. See survey.apps.AppConfig'.format(
                    self.current_survey_label, site_surveys.get_survey_names(*self.active_survey_schedule_groups)))
        sys.stdout.write(' * current survey is {}.\n'.format(self.current_survey_label))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    def current_survey(self):
        """Returns the current survey instance."""
        return site_surveys.get_survey(self.current_survey_name)
