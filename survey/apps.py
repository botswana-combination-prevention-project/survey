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

    def __repr__(self):
        return '{0}({1.label})'.format(self.__class__.__name__, self)

    def __str__(self):
        return self.label


class CurrentSurveys:
    def __init__(self, *current_surveys):
        self.current_surveys = current_surveys
        labels = []
        map_areas = []
        for current_survey in current_surveys:
            labels.append(current_survey.label)
            map_areas.append(current_survey.map_area)
        labels.sort()
        self.labels = labels
        map_areas = list(set(map_areas))
        if len(map_areas) > 1:
            raise SurveyError('All current surveys must be in the same map_area. Got {}.'.format(map_areas))
        self.map_area = map_areas[0]

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
                'Current surveys listed in AppConfig do not correspond with any surveys in surveys.py. '
                'Got: \n *{}\n Expected one of: \n *{}\n See survey.apps.AppConfig and surveys.py'.format(
                    ',\n *'.join(self.current_surveys.labels),
                    ',\n *'.join([s.label for s in site_surveys.surveys])))
        sys.stdout.write(' * current surveys are:.\n')
        for current_survey in self.current_surveys:
            sys.stdout.write('   - {}.\n'.format(current_survey.label))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
