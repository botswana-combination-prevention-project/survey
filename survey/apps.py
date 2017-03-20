# coding=utf-8

import sys

from django.apps import AppConfig as DjangoApponfig
from django.conf import settings
from django.core.management.color import color_style

from .exceptions import SurveyError
from .site_surveys import site_surveys
from .sparser import S

style = color_style()


class AppConfig(DjangoApponfig):
    name = 'survey'

    use_settings = False

    # format is S(group.survey_schedule.survey.map_area)
    current_surveys = [
        S('test_survey.year-1.baseline.test_community'),
        S('test_survey.year-1.annual-1.test_community'),
        S('test_survey.year-1.annual-2.test_community')]

    @property
    def current_survey_schedule(self):
        try:
            survey_group = settings.SURVEY_GROUP_NAME
        except AttributeError:
            survey_group = 'test_survey'
        try:
            survey_schedule = settings.SURVEY_SCHEDULE_NAME
        except AttributeError:
            survey_schedule = 'year-1'
        try:
            map_area = settings.CURRENT_MAP_AREA
        except AttributeError:
            map_area = 'test_community'
        return '{}.{}.{}'.format(survey_group, survey_schedule, map_area)

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_surveys.autodiscover()
        if site_surveys.loaded:
            try:
                # use same format as above
                self.current_surveys = settings.CURRENT_SURVEYS
            except AttributeError as e:
                if self.use_settings:
                    raise AttributeError(
                        '{} See survey.AppConfig.'.format(str(e)))
            else:
                if not self.use_settings:
                    sys.stdout.write(style.ERROR(
                        ' * overriding app_config. Using settings.'
                        'CURRENT_SURVEYS.\n Set AppConfig.use_settings '
                        '= True to suppress this warning\n'))
            site_surveys.register_current(*self.current_surveys)
        if (self.current_survey_schedule
                and self.current_survey_schedule
                not in site_surveys.get_survey_schedule_field_values()):
            raise SurveyError(
                'Invalid current survey schedule specified. See AppConfig. '
                'Got \'{}\'. Expected one of {}.'.format(
                    self.current_survey_schedule,
                    site_surveys.get_survey_schedule_field_values()))
        else:
            sys.stdout.write(
                ' * current survey schedule : {}\n'.format(
                    self.current_survey_schedule or '<not set>'))
        sys.stdout.write(' * detected survey schedules are:\n')
        for field_value in site_surveys.get_survey_schedule_field_values():
            sys.stdout.write('   - {}\n'.format(field_value))
        sys.stdout.write(' * current surveys are:\n')
        for survey in site_surveys.current_surveys:
            sys.stdout.write('   - {}\n'.format(survey.field_value))
        sys.stdout.write(' * detected map_areas: \'{}\'\n'.format(
            ', '.join(site_surveys.current_map_areas)))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
