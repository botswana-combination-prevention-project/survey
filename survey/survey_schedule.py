# coding=utf-8
import arrow

from .mixins import MapAreaMixin, DateMixin
from .exceptions import AddSurveyDateError, AddSurveyMapAreaError, AddSurveyNameError


class SurveySchedule(MapAreaMixin, DateMixin):

    def __init__(self, name=None, group_name=None, start=None, end=None,
                 map_area=None, map_areas=None):
        self.name = name  # e.g. year-1, year-2, ...
        super().__init__(map_area=map_area, map_areas=map_areas, start=start, end=end)
        self.registry = []
        self.group_name = group_name  # e.g. ESS
        self.survey_groups = []

    def __str__(self):
        return self.label

    @property
    def rstart(self):
        return arrow.Arrow.fromdatetime(self.start, self.start.tzinfo).to('utc')

    @property
    def rend(self):
        return arrow.Arrow.fromdatetime(self.end, self.end.tzinfo).to('utc')

    @property
    def label(self):
        return '{}.{}'.format(self.group_name, self.name)

    @property
    def surveys(self):
        """Returns all surveys in the schedule."""
        return self.registry

    @property
    def field_value(self):
        return '{}.{}.{}'.format(self.group_name, self.name, self.map_area)

    @property
    def current_surveys(self):
        """Returns the surveys in the schedule that, according to app_config, are current."""
        return [survey for survey in self.registry if survey.current]

    @property
    def current(self):
        return self.current_surveys

    @property
    def previous(self):
        """Returns the previous current survey or None."""
        from .site_surveys import site_surveys
        return site_surveys.previous_survey_schedule(self)

    @property
    def next(self):
        """Returns the next current survey or None."""
        from .site_surveys import site_surveys
        return site_surveys.next_survey_schedule(self)

    def add_survey(self, *surveys):
        for survey in surveys:
            if not (self.start <= survey.start <= self.end):
                raise AddSurveyDateError(
                    'Unable to add survey to schedule {}. Survey {}.start is invalid. '
                    'Got {}.'.format(self.name, survey.name, self.start.strftime('%Y-%m-%d %Z')))
            if not (self.start <= survey.end <= self.end):
                raise AddSurveyDateError(
                    'Unable to add survey to schedule {}. Survey {}.end is invalid. '
                    'Got {}.'.format(self.name, survey.name, self.start.strftime('%Y-%m-%d %Z')))
            if survey.name in self.registry:
                raise AddSurveyNameError(
                    'Unable to add survey to schedule {}. A Survey with for map_area has already been '
                    'added. Got {}.'.format(self.name, survey.name))
            if survey.map_area in self.registry:
                raise AddSurveyMapAreaError(
                    'Unable to add survey to schedule {}. A Survey with for map_area has already been '
                    'added . Got {}.'.format(self.name, survey.name))
            if self.map_areas:
                if survey.map_area not in self.map_areas:
                    raise AddSurveyMapAreaError(
                        'Unable to add survey to schedule. Invalid map_area for '
                        'schedule {}. Got {}.'.format(
                            self.name, survey.map_area))
#             if self.get_surveys(map_area=survey.map_area, reference_date=survey.start):
#                 raise AddSurveyOverlapError()
            survey.survey_schedule = self
            self.registry.append(survey)
        self._reorder()

    def _reorder(self):
        """Keeps the registry ordered."""
        self.registry.sort(key=lambda x: x.start)

    def get_surveys(self, map_area=None, reference_datetime=None):
        """Returns a list of surveys that meet the criteria."""
        def in_datetime_range(survey, reference_datetime):
            if survey.start <= reference_datetime <= survey.end:
                return True
            return False
        surveys = []
        if reference_datetime and map_area:
            surveys = [
                s for s in self.registry
                if s.map_area == map_area and in_datetime_range(s, reference_datetime)]
        elif map_area:
            surveys = [s for s in self.registry if s.map_area == map_area]
        elif reference_datetime:
            surveys = [s for s in self.registry if in_datetime_range(s, reference_datetime)]
        surveys.sort(key=lambda x: x.start)
        return surveys
