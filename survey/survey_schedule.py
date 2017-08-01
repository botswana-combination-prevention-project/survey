# coding=utf-8
from .exceptions import AddSurveyDateError, AddSurveyMapAreaError, AddSurveyNameError
from .helpers import DateHelper, MapAreaHelper, DateError
from .sparser import S


class SurveyScheduleError(Exception):
    pass


class SurveyScheduleDateError(Exception):
    pass


class AddSurveyPositionError(Exception):
    pass


class SurveySchedule:

    date_helper_cls = DateHelper
    map_area_helper_cls = MapAreaHelper

    def __init__(self, name=None, group_name=None, start=None, end=None,
                 map_area=None, map_areas=None):
        self.name = name
        self.registry = []
        self.group_name = group_name
        self.survey_groups = []
        self.current = False

        try:
            self.date_helper = self.date_helper_cls(start=start, end=end)
        except DateError as e:
            raise SurveyScheduleError(e)
        self.start = self.date_helper.start
        self.end = self.date_helper.end
        self.rstart = self.date_helper.rstart
        self.rend = self.date_helper.rend

        self.map_area_helper = self.map_area_helper_cls(
            map_area=map_area, map_areas=map_areas)
        self.map_area = self.map_area_helper.map_area
        self.map_areas = self.map_area_helper.map_areas
        self.map_area_display = self.map_area_helper.map_area_display

    def __str__(self):
        return self.field_value

    def __repr__(self):
        start = self.start.strftime('%Y-%m-%d %Z')
        end = self.end.strftime('%Y-%m-%d %Z')
        return f'{self.__class__.__name__}(\'{self.field_value}\', {start}, {end})'

    def to_sparsers(self):
        sparsers = []
        for survey in self.surveys:
            sparsers.append(
                S(f'{self.group_name}.{self.name}.{survey.name}.{self.map_area}'))
        return sparsers

    @property
    def short_name(self):
        return f'{self.group_name}.{self.name}'

    @property
    def surveys(self):
        """Returns all surveys in the schedule.
        """
        if not self.registry:
            raise SurveyScheduleError(
                f'SurveySchedule has no surveys!. Got {repr(self)}.')
        return self.registry

    @property
    def field_value(self):
        return f'{self.group_name}.{self.name}.{self.map_area}'

    @property
    def current_surveys(self):
        """Returns the surveys in the schedule that, according
        to app_config, are current.
        """
        return [survey for survey in self.registry if survey.current]

    def get_survey(self, name):
        """Returns the surveys in the schedule that, according to
        app_config, are current.
        """
        surveys = [survey for survey in self.surveys if survey.name == name]
        try:
            return surveys[0]
        except IndexError:
            return None

    @property
    def previous(self):
        """Returns the previous survey schedule or None.
        """
        from .site_surveys import site_surveys
        return site_surveys.previous_survey_schedule(self)

    @property
    def next(self):
        """Returns the next survey schedule or None.
        """
        from .site_surveys import site_surveys
        return site_surveys.next_survey_schedule(self)

    def add_survey(self, *surveys):
        for survey in surveys:
            if survey.position is None:
                raise AddSurveyPositionError(
                    f'Unable to add survey to schedule \'{self.name}\'. Survey position '
                    f'is invalid. Got {survey.position}. See survey \'{survey.name}\'')
            if not (self.start <= survey.start <= self.end):
                raise AddSurveyDateError(
                    'Unable to add survey to schedule {}. Survey {}.start '
                    'is invalid. Got {}.'.format(
                        self.name, survey.name,
                        self.start.strftime('%Y-%m-%d %Z')))
            if not (self.start <= survey.end <= self.end):
                raise AddSurveyDateError(
                    'Unable to add survey to schedule {}. Survey {}.end '
                    'is invalid. Got {}.'.format(
                        self.name,
                        survey.name,
                        self.start.strftime('%Y-%m-%d %Z')))
            if survey.name in self.registry:
                raise AddSurveyNameError(
                    'Unable to add survey to schedule {}. A Survey with '
                    'for map_area has already been added. Got {}.'.format(
                        self.name, survey.name))
            if survey.map_area in self.registry:
                raise AddSurveyMapAreaError(
                    'Unable to add survey to schedule {}. A Survey with '
                    'for map_area has already been added . Got {}.'.format(
                        self.name, survey.name))
            if self.map_areas:
                if survey.map_area not in self.map_areas:
                    raise AddSurveyMapAreaError(
                        'Unable to add survey to schedule. Invalid '
                        'map_area for schedule \'{}\'. Got \'{}\'.'.format(
                            self.name, survey.map_area))
            survey.survey_schedule = self
            self.registry.append(survey)

        # keep the registry ordered
        self.registry.sort(key=lambda x: x.position)

    def get_surveys(self, map_area=None, reference_datetime=None):
        """Returns a list of surveys that meet the criteria.
        """
        def in_datetime_range(survey, reference_datetime):
            if survey.start <= reference_datetime <= survey.end:
                return True
            return False
        surveys = []
        if reference_datetime and map_area:
            surveys = [
                s for s in self.registry
                if s.map_area == map_area
                and in_datetime_range(s, reference_datetime)]
        elif map_area:
            surveys = [s for s in self.registry if s.map_area == map_area]
        elif reference_datetime:
            surveys = [
                s for s in self.registry
                if in_datetime_range(s, reference_datetime)]
        surveys.sort(key=lambda x: x.start)
        return surveys
