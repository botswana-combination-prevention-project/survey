# coding=utf-8

import sys
import copy

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from .exceptions import AddSurveyDateError, AddSurveyMapAreaError
from .exceptions import AddSurveyOverlapError, AddSurveyNameError
from .helpers import CurrentSurveysHelper
from .sparser import S
from survey.sparser import SurveyParserError


class CurrentSurveySchedulesAlreadyLoaded(Exception):
    pass


class SiteSurveysRegistryNotLoaded(Exception):
    pass


class SiteSurveysError(Exception):
    pass


class SiteSurveysAlreadyRegistered(Exception):
    pass


class SiteSurveys:
    """Main controller of :class:`SurveySchedule` objects.

    A survey_schedule contains surveys.
    """

    current_surveys_helper = CurrentSurveysHelper

    def __init__(self):
        self._registry = []
        self.loaded = False
        self.loaded_current = False
        self.current_survey_schedules = []
        self.current_surveys = []
        self.constants = {}

    @property
    def registry(self):
        if not self.loaded:
            raise SiteSurveysRegistryNotLoaded(
                'Registry not loaded. Is AppConfig for \'survey\' '
                'declared in settings?.')
        return self._registry

    def register(self, survey_schedule):
        self.loaded = True
        if not survey_schedule.surveys:
            raise SiteSurveysError(
                f'Not registering survey schedule. Survey schedule has no surveys. '
                f'Got {repr(survey_schedule)}')
        elif survey_schedule.name in [
                survey_schedule.name for survey_schedule in self.registry]:
            raise SiteSurveysAlreadyRegistered(
                f'Survey Schedule {repr(survey_schedule)} is already registered.')
        for schedule in self.get_survey_schedules(
                group_name=survey_schedule.group_name):
            if survey_schedule.start == schedule.start:
                raise SiteSurveysAlreadyRegistered(
                    'Survey Schedule {} is already registered using '
                    'start date {}. Unable to registered {}.'.format(
                        schedule.name,
                        survey_schedule.start.strftime('%Y-%m-%d'),
                        survey_schedule.name))
        self.registry.append(survey_schedule)

    def register_current(self, *survey_schedules):
        """Registers the current surveys from survey_schedule(s)
        or sparser.S objects.
        """
        if self.loaded_current:
            raise CurrentSurveySchedulesAlreadyLoaded(
                'Current survey schedules are already loaded.')
        else:
            helper = self.current_surveys_helper(
                current_survey_schedules=survey_schedules,
                registered_survey_schedules=self.get_survey_schedules())
            self.current_survey_schedules = helper.current_survey_schedules
            self.current_surveys = helper.current_surveys
            self.loaded_current = True

    def get_survey_schedule(self, value):
        """Returns a survey schedule object or raises and exception.
        """
        try:
            group_name, survey_schedule_name, _ = value.split('.')
        except ValueError:
            group_name, survey_schedule_name = value.split('.')
        survey_schedule = None
        for item in self.registry:
            if (item.name == survey_schedule_name
                    and item.group_name == group_name):
                survey_schedule = item
                break
        if not survey_schedule:
            raise SiteSurveysError(
                f'Unable to find a registered survey schedule matching '
                f'group_name={group_name} and '
                f'survey_schedule_name={survey_schedule_name}.')
        return survey_schedule

    def get_survey_schedule_from_field_value(self, field_value):
        """Returns a survey schedule or raises using the SurveySchedule
        field_value attr.
        """
        return self.get_survey_schedule(field_value)

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
            schedules = [
                s for s in schedules if s in self.current_survey_schedules]
        schedules.sort(key=lambda o: o.start)
        return schedules

    def get_survey(self, field_value, current=None):
        """Returns a survey object using the long name.
        """
        try:
            surveys = [
                survey for survey in self.surveys
                if survey.field_value == field_value]
            if current:
                return [survey for survey in surveys
                        if survey in self.current_surveys][0]
            else:
                return surveys[0]
        except IndexError:
            return None

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

    def get_survey_schedule_field_values(self):
        field_values = []
        for survey_schedule in self.get_survey_schedules():
            field_values.append(survey_schedule.field_value)
        field_values.sort()
        return field_values

    def get_survey_from_field_value(self, field_value):
        try:
            s = S(field_value)
        except SurveyParserError:
            found = None
        else:
            found = None
            survey_schedule = self.get_survey_schedule(
                '.'.join([s.group_name, s.survey_schedule_name]))
            for survey in survey_schedule.surveys:
                if survey.name == s.survey_name and survey.map_area == s.map_area:
                    found = survey
                    break
            if not found:
                if not django_apps.get_app_config('edc_device').is_client:
                    for survey in survey_schedule.surveys:
                        if survey.name == s.survey_name:
                            found = survey
                            break
                else:
                    raise SiteSurveysError(
                        f'Invalid survey for {repr(survey_schedule)}. '
                        f'Got survey.field_value=\'{s.field_value}\'. '
                        f'Expected one of '
                        f'{[s.field_value for s in survey_schedule.surveys]}')
        return found

    @property
    def map_areas(self):
        """Extracts ALL map_areas listed in surveys registered
        to the system.
        """
        map_areas = []
        for survey in self.surveys:
            map_areas.append(survey.map_area)
        return list(set(map_areas))

    @property
    def current_map_areas(self):
        """Extracts map_areas listed in current surveys.
        """
        map_areas = []
        for survey in self.current_surveys:
            map_areas.append(survey.map_area)
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
        """Returns the next survey schedule in this group or None.

        Ordered by start (date).
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
                except (SiteSurveysError,
                        SiteSurveysAlreadyRegistered,
                        SiteSurveysError,
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
