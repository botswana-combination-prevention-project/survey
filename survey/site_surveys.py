# coding=utf-8

import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from survey.exceptions import (
    SurveyScheduleError, RegistryNotLoaded, AlreadyRegistered, SurveyError, AddSurveyDateError,
    AddSurveyMapAreaError, AddSurveyOverlapError, AddSurveyNameError)


class SiteSurveys:

    """ Main controller of :class:`SurveySchedule` objects.

    A survey_schedule contains surveys"""

    def __init__(self):
        self._registry = []
        self.loaded = False

    @property
    def registry(self):
        if not self.loaded:
            raise RegistryNotLoaded(
                'Registry not loaded. Is AppConfig for \'survey\' declared in settings?.')
        return self._registry

    def clear_registry(self):
        self._registry = []
        self.loaded = False

    def register(self, survey_schedule):
        self.loaded = True
        if survey_schedule.name in [survey_schedule.name for survey_schedule in self.registry]:
            raise AlreadyRegistered('Survey Schedule {} is already registered.'.format(survey_schedule))
        for schedule in self.get_survey_schedules(group_name=survey_schedule.group_name):
            if survey_schedule.start_date == schedule.start_date:
                raise AlreadyRegistered(
                    'Survey Schedule {} is already registered using start date {}. '
                    'Unable to registered {}.'.format(
                        schedule.name, survey_schedule.start_date.strftime('%Y-%m-%d'), survey_schedule.name))
        self.registry.append(survey_schedule)

    def get_survey_schedule(self, name):
        group_name, name = name.split('.')
        try:
            survey_schedule = [s for s in self.registry if s.name == name and s.group_name == group_name][0]
        except IndexError:
            raise SurveyScheduleError(
                'Invalid survey schedule name. Got \'{}\'. Possible names are [{}].'.format(
                    name, ', '.join([s.name for s in self.registry])))
        return survey_schedule

    def get_survey_schedules(self, group_name=None):
        """Returns a [<list of survey_schedules>].

        None is a valid group_name that returns all survey_schedules."""
        schedules = []
        if group_name:
            for survey_schedule in self.registry:
                if survey_schedule.group_name == group_name:
                    schedules.append(survey_schedule)
        else:
            schedules = self.registry
        schedules.sort(key=lambda o: o.start_date)
        return schedules

    def get_surveys(self, *current_surveys):
        surveys = []
        for current_survey in current_surveys:
            for survey_schedule in self.get_survey_schedules():
                if survey_schedule.name == current_survey.survey_schedule:
                    for survey in survey_schedule.surveys:
                        if survey.name == current_survey.survey_name and survey.map_area == current_survey.map_area:
                            surveys.append(survey)
        return surveys

    @property
    def surveys(self):
        """Returns an ordered list of surveys."""
        surveys = []
        for survey_schedule in self.get_survey_schedules():
            for survey in survey_schedule.surveys:
                surveys.append(survey)
        if surveys:
            surveys.sort(key=lambda x: x.survey_schedule.split('.')[0] + str(x.position))
        return surveys

    def get_survey_names(self, *group_names):
        survey_names = []
        for group_name in group_names:
            for survey_schedule in self.get_survey_schedules(group_name=group_name):
                for survey in survey_schedule.surveys:
                    survey_names.append(survey.label)
        return survey_names

    def get_survey_schedule_group_names(self):
        group_names = []
        survey_schedule_collection = self.get_survey_schedules()
        for survey_schedule in survey_schedule_collection:
            group_names.append(survey_schedule.group_name)
        return group_names

    def get_survey_from_full_label(self, label):
        group_name, survey_schedule_name, survey_name, map_area = label.split('.')
        survey_schedule = self.get_survey_schedule('.'.join([group_name, survey_schedule_name]))
        for survey in survey_schedule.surveys:
            if survey.name == survey_name and survey.map_area == map_area:
                return survey
        return None

    def autodiscover(self, module_name=None):
        """Autodiscovers classes in the surveys.py file of any INSTALLED_APP."""
        module_name = module_name or 'surveys'
        sys.stdout.write(' * checking for site {} ...\n'.format(module_name))
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_surveys._registry)
                    import_module('{}.{}'.format(app, module_name))
                    sys.stdout.write(' * registered surveys from application \'{}\'\n'.format(app))
                except (SurveyScheduleError, AlreadyRegistered, SurveyError,
                        AddSurveyDateError, AddSurveyMapAreaError, AddSurveyNameError, AddSurveyOverlapError):
                    raise
                except Exception as e:
                    if 'No module named \'{}.{}\''.format(app, module_name) not in str(e):
                        raise Exception(e)
                    site_surveys._registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ImportError:
                pass

site_surveys = SiteSurveys()
