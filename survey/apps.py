# coding=utf-8

import sys

from django.apps import AppConfig as DjangoApponfig
from django.conf import settings
from django.core.management.color import color_style

from .site_surveys import site_surveys
from survey.exceptions import SurveyError

style = color_style()


class CurrentSurvey:
    def __init__(self, label):
        self.label = label
        self.group_name, self.survey_schedule, self.survey_name, self.map_area = label.split('.')


class CurrentSurveys:
    def __init__(self, *current_surveys):
        labels = []
        for current_survey in current_surveys:
            labels.append(current_survey.label)
        labels.sort()
        self.label = labels
        self.current_surveys = current_surveys

    def __iter__(self):
        for current_survey in self.current_surveys:
            yield current_survey


class AppConfig(DjangoApponfig):
    name = 'survey'
    current_surveys = CurrentSurveys(*[
        CurrentSurvey('test_survey.year-1.baseline.test_community'),
        CurrentSurvey('test_survey.year-1.annual-1.test_community'),
        CurrentSurvey('test_survey.year-1.annual-2.test_community')])

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_surveys.autodiscover()
        try:
            self.current_surveys = settings.CURRENT_SURVEYS
        except AttributeError:
            pass
        for current_survey in self.current_surveys:
            if not site_surveys.get_survey_schedules(group_name=current_survey.group_name):
                raise SurveyError(
                    'Invalid group name. Got \'{}\'. Expected one of {}. See survey.apps.AppConfig'.format(
                        current_survey.group_name, site_surveys.get_survey_schedule_group_names()))
        if not site_surveys.get_surveys(*self.current_surveys):
            raise SurveyError(
                'Invalid current surveys. Got \'{}\'. Expected one of {}. See survey.apps.AppConfig'.format(
                    ', '.join([c.survey_name for c in self.current_surveys]),
                    self.current_surveys, site_surveys.get_survey_names(*self.active_survey_schedule_groups)))
        sys.stdout.write(' * current surveys are:.\n')
        for current_survey in self.current_surveys:
            sys.stdout.write('   - {}.\n'.format(current_survey.label))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
