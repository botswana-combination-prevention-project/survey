# coding=utf-8

import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from .exceptions import (
    SurveyScheduleError, RegistryNotLoaded, AlreadyRegistered,
    SurveyError, AddSurveyDateError,
    AddSurveyMapAreaError, AddSurveyOverlapError, AddSurveyNameError)
from .sparser import S


class SiteSurveys:
    """Main controller of :class:`SurveySchedule` objects.

    A survey_schedule contains surveys
    """

    def __init__(self):
        self._registry = []
        self.loaded = False
        self.loaded_current = False
        self.current_surveys = []
        self._backup_registry = []
        self._backup_current_surveys = []
        self.constants = {}

    @property
    def registry(self):
        if not self.loaded:
            raise RegistryNotLoaded(
                'Registry not loaded. Is AppConfig for \'survey\' '
                'declared in settings?.')
        return self._registry

    def backup_registry(self, clear=False):
        self._backup_current_surveys = copy.deepcopy(self.current_surveys)
        self._backup_registry = copy.deepcopy(self._registry)
        if clear:
            self._registry = []
            self.current_surveys = []
            self.loaded = False
            self.loaded_current = False

    def restore_registry(self):
        self._registry = copy.deepcopy(self._backup_registry)
        self.current_surveys = copy.deepcopy(self._backup_current_surveys)
        self._backup_registry = []
        self._backup_current_surveys = []
        self.loaded = True
        self.loaded_current = True

    def unregister(self, survey_schedule):
        try:
            self._registry.remove(survey_schedule)
        except ValueError:
            pass

    def register(self, survey_schedule):
        self.loaded = True
        if survey_schedule.name in [
                survey_schedule.name for survey_schedule in self.registry]:
            raise AlreadyRegistered(
                'Survey Schedule {} is already registered.'.format(
                    survey_schedule))
        for schedule in self.get_survey_schedules(
                group_name=survey_schedule.group_name):
            if survey_schedule.start == schedule.start:
                raise AlreadyRegistered(
                    'Survey Schedule {} is already registered using '
                    'start date {}. Unable to registered {}.'.format(
                        schedule.name,
                        survey_schedule.start.strftime('%Y-%m-%d'),
                        survey_schedule.name))
        self.registry.append(survey_schedule)

    def register_current(self, *slist):
        if not self.loaded:
            raise RegistryNotLoaded(
                'Registry not loaded. Register ALL surveys before '
                'registering the current surveys.')
        for s in slist:
            if not self.get_survey_schedules(group_name=s.group_name):
                try:
                    survey_schedule_group_names = self.get_survey_schedule_group_names()
                    raise SurveyError(
                        'Invalid group name. Got \'{}\'. Expected one of {}. '
                        'See survey.apps.AppConfig'.format(
                            s.group_name, survey_schedule_group_names))
                except AttributeError as e:
                    raise SurveyError(
                        'Have you installed any surveys?. '
                        'See survey.apps.AppConfig '
                        'and surveys.py. Got {}'.format(
                            str(e)))
        if not self.get_surveys(*slist):
            raise SurveyError(
                'Current surveys listed in AppConfig do not correspond '
                'with any surveys in surveys.py. Got: \n *{}\n Expected one '
                'of: \n *{}\n See survey.apps.AppConfig and surveys.py'.format(
                    ',\n *'.join([s.name for s in slist]),
                    ',\n *'.join([s.field_value for s in self.surveys])))
        for survey in self.surveys:
            if survey.long_name in [s.name for s in slist]:
                survey.current = True
                self.current_surveys.append(survey)
        self.current_surveys.sort(key=lambda x: x.start)

    def get_survey_schedule(self, value):
        """Returns a survey schedule object or raises and exception.
        """
        group_name, name = value.split('.')
        try:
            survey_schedule = [
                s for s in self.registry
                if s.name == name and s.group_name == group_name][0]
        except IndexError:
            raise SurveyScheduleError(
                'Invalid survey schedule name. Got \'{}\'. '
                'Possible names are [{}].'.format(
                    name, ', '.join([s.name for s in self.registry])))
        return survey_schedule

    def get_survey_schedule_from_field_value(self, field_value):
        if field_value:
            s = S(field_value)
            return self.get_survey_schedule('{}.{}'.format(
                s.group_name, s.survey_schedule_name))
        return None

    def get_survey_schedules(self, group_name=None, current=None):
        """Returns a [<list of survey_schedules>].

        None is a valid group_name that returns all survey_schedules.
        """
        schedules = []
        if group_name:
            for survey_schedule in self.registry:
                if survey_schedule.group_name == group_name:
                    schedules.append(survey_schedule)
        else:
            schedules = self.registry
        if current:
            schedules = [s for s in schedules if s.current]
        schedules.sort(key=lambda o: o.start)
        return schedules

    def get_survey(self, field_value, current=None):
        """Returns a survey object using the long name.
        """
        try:
            surveys = [
                survey for survey in self.surveys if survey.field_value == field_value]
            if current:
                return [survey for survey in surveys if survey.current][0]
            else:
                return surveys[0]
        except IndexError:
            return None

    def get_surveys(self, *surveys, current=None):
        selected = []
        for item in surveys:
            for survey_schedule in self.get_survey_schedules():
                if survey_schedule.name == item.survey_schedule_name:
                    for survey in survey_schedule.surveys:
                        if (survey.name == item.survey_name and
                                survey.map_area == item.map_area):
                            selected.append(survey)
        if current:
            return [survey for survey in selected if survey.current]
        return selected

    @property
    def surveys(self):
        """Returns an ordered list of all surveys registered with the system.

        See also `current_surveys`.
        """
        surveys = []
        for survey_schedule in self.get_survey_schedules():
            for survey in survey_schedule.surveys:
                surveys.append(survey)
        surveys.sort(key=lambda x: x.start)
        return surveys

    def get_survey_names(self, *group_names):
        survey_names = []
        if group_names:
            for group_name in group_names:
                for survey_schedule in self.get_survey_schedules(
                        group_name=group_name):
                    for survey in survey_schedule.surveys:
                        survey_names.append(survey.field_value)
        else:
            for survey_schedule in self.get_survey_schedules():
                for survey in survey_schedule.surveys:
                    survey_names.append(survey.field_value)
        return survey_names

    def get_survey_schedule_group_names(self):
        group_names = []
        survey_schedule_collection = self.get_survey_schedules()
        for survey_schedule in survey_schedule_collection:
            group_names.append(survey_schedule.group_name)
        return group_names

    def get_survey_schedule_field_values(self):
        field_values = []
        for survey_schedule in self.get_survey_schedules():
            field_values.append(survey_schedule.field_value)
        field_values.sort()
        return field_values

    def get_survey_from_field_value(self, field_value):
        if field_value:
            s = S(field_value)
            survey_schedule = self.get_survey_schedule(
                '.'.join([s.group_name, s.survey_schedule_name]))
            for survey in survey_schedule.surveys:
                if survey.name == s.survey_name and survey.map_area == s.map_area:
                    return survey
            if not django_apps.get_app_config('edc_device').is_client:
                for survey in survey_schedule.surveys:
                    if survey.name == s.survey_name:
                        return survey
            else:
                raise SurveyError(
                    'Invalid survey name for survey_schedule \'{}\'. Got \'{}\'. '
                    'Expected one of {}'.format(
                        survey_schedule.field_value,
                        s.field_value,
                        [s.field_value for s in survey_schedule.surveys]))
        return None

    @property
    def map_areas(self):
        """Extracts ALL map_areas listed in surveys registered
        to the system.
        """
        map_areas = []
        for s in self.surveys:
            map_areas.append(s.map_area)
        return list(set(map_areas))

    @property
    def current_map_areas(self):
        """Extracts map_areas listed in current surveys.
        """
        map_areas = []
        for s in self.current_surveys:
            map_areas.append(s.map_area)
        return list(set(map_areas))

    def previous_survey_schedule(self, survey_schedule):
        """Returns the previous survey schedule or None.
        """
        previous_survey_schedules = [
            s for s in self.get_survey_schedules(
                group_name=survey_schedule.group_name)
            if s.start < survey_schedule.start]
        try:
            return previous_survey_schedules[-1:][0]
        except IndexError:
            return None

    def next_survey_schedule(self, survey_schedule):
        """Returns the next survey schedule or None.
        """
        next_survey_schedules = [s for s in self.get_survey_schedules(
            group_name=survey_schedule.group_name)
            if s.start > survey_schedule.start]
        try:
            return next_survey_schedules[0]
        except IndexError:
            return None

    def previous_survey(self, survey):
        previous_surveys = [
            s for s in self.current_surveys if s.start < survey.start]
        try:
            return previous_surveys[-1:][0]
        except IndexError:
            return None

    def next_survey(self, survey):
        """Returns the next current survey or None.
        """
        next_surveys = [
            s for s in self.current_surveys if s.start > survey.start]
        try:
            return next_surveys[0]
        except IndexError:
            return None

    def autodiscover(self, module_name=None):
        """Autodiscovers classes in the surveys.py file of any
        INSTALLED_APP.
        """
        module_name = module_name or 'surveys'
        sys.stdout.write(' * checking for site {} ...\n'.format(module_name))
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_surveys._registry)
                    import_module('{}.{}'.format(app, module_name))
                    sys.stdout.write(
                        ' * registered surveys from application '
                        '\'{}\'\n'.format(app))
                except (SurveyScheduleError,
                        AlreadyRegistered,
                        SurveyError,
                        AddSurveyDateError,
                        AddSurveyMapAreaError,
                        AddSurveyNameError,
                        AddSurveyOverlapError):
                    raise
                except Exception as e:
                    if 'No module named \'{}.{}\''.format(
                            app, module_name) not in str(e):
                        raise Exception(e)
                    site_surveys._registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ImportError:
                pass


site_surveys = SiteSurveys()
