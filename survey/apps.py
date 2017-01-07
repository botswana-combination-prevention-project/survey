# coding=utf-8

import sys

from django.apps import AppConfig as DjangoApponfig
from django.conf import settings
from django.core.management.color import color_style

from .site_surveys import site_surveys

style = color_style()


class S:
    def __init__(self, s, inactive=None):
        self.group_name, self.survey_schedule_name, self.survey_name, self.map_area = s.split('.')
        self.name = s
        self.inactive = inactive

    def __str__(self):
        return '{}{}'.format(self.name, '' if not self.inactive else ' - inactive')


class AppConfig(DjangoApponfig):
    name = 'survey'

    use_settings = False

    # format is S(group.survey_schedule.survey.map_area)
    current_surveys = [
        S('test_survey.year-1.baseline.test_community'),
        S('test_survey.year-1.annual-1.test_community'),
        S('test_survey.year-1.annual-2.test_community')]

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_surveys.autodiscover()
        if site_surveys.loaded:
            try:
                self.current_surveys = settings.CURRENT_SURVEYS  # use same format as above
            except AttributeError as e:
                if self.use_settings:
                    raise AttributeError('{} See survey.AppConfig.'.format(str(e)))
            else:
                if not self.use_settings:
                    sys.stdout.write(style.ERROR(
                        ' * overriding app_config. Using settings.CURRENT_SURVEYS.\n'
                        '   Set AppConfig.use_settings = True to suppress this warning\n'))
            site_surveys.register_current(*self.current_surveys)
        sys.stdout.write(' * current surveys are:.\n')
        for survey in site_surveys.current_surveys:
            sys.stdout.write('   - {}\n'.format(survey.field_name))
        sys.stdout.write(' * detected map_areas: \'{}\'\n'.format(', '.join(site_surveys.current_map_areas)))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
