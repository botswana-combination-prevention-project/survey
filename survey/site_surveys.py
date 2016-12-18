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
        self._registry = {}
        self.loaded = False

    @property
    def registry(self):
        if not self.loaded:
            raise RegistryNotLoaded(
                'Registry not loaded. Is AppConfig for \'survey\' declared in settings?.')
        return self._registry

    def register(self, survey_schedule):
        self.loaded = True
        if survey_schedule.name in self.registry:
            raise AlreadyRegistered('Survey Schedule {} is already registered.'.format(survey_schedule))
        for schedules in self.get_survey_schedules(group_name=survey_schedule.group_name).values():
            for schedule in schedules:
                if survey_schedule.start_date == schedule.start_date:
                    raise AlreadyRegistered(
                        'Survey Schedule {} is already registered using start date {}. '
                        'Unable to registered {}.'.format(
                            schedule.name, survey_schedule.start_date.strftime('%Y-%m-%d'), survey_schedule.name))
        self.registry.update({survey_schedule.name: survey_schedule})

    def get_survey_schedule(self, name):
        name = name.split('.')[0]
        try:
            survey_schedule = self.registry[name]
        except KeyError:
            raise SurveyScheduleError(
                'Invalid survey schedule name. Got \'{}\'. Possible names are [{}].'.format(
                    name, ', '.join(self.registry.keys())))
        return survey_schedule

    def get_survey_schedules(self, group_name=None):
        """Returns a dictionary of {group_name: [<list of survey_schedules>]}.

        None is a valid group_name that returns all survey_schedules."""
        ret = {}
        schedules = []
        if group_name:
            for survey_schedule in self.registry.values():
                if survey_schedule.group_name == group_name:
                    schedules.append(survey_schedule)
            schedules.sort(key=lambda o: o.start_date)
            ret = {group_name: schedules}
        else:
            for survey_schedule in self.registry.values():
                schedules.append(survey_schedule)
            schedules.sort(key=lambda o: o.start_date)
            ret = {group_name: schedules}
        return ret

    def get_survey(self, survey_schedule_name):
        return self.registry[survey_schedule_name].surveys

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
