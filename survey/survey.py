# coding=utf-8

import arrow

from .exceptions import SurveyError
from .helpers import DateHelper, MapAreaHelper
from .sparser import S
from survey.helpers.date_helper import DateError


class DummySurvey:
    survey_breadcrumbs = []
    map_area_display = None
    short_name = None
    field_value = None


class Survey:

    date_helper_cls = DateHelper
    map_area_helper_cls = MapAreaHelper

    def __init__(self, name=None, start=None, end=None,
                 full_enrollment_datetime=None, position=None,
                 map_area=None, map_areas=None):
        self.name = name
        self.survey_name = name
        self.current = None
        self.survey_schedule = None  # set when registered to a survey_schedule
        self.position = position

        try:
            self.date_helper = self.date_helper_cls(start=start, end=end)
        except DateError as e:
            raise SurveyError(e)
        self.start = self.date_helper.start
        self.end = self.date_helper.end
        self.rstart = self.date_helper.rstart
        self.rend = self.date_helper.rend

        self.map_area_helper = self.map_area_helper_cls(
            map_area=map_area, map_areas=map_areas)
        self.map_area = self.map_area_helper.map_area
        self.map_areas = self.map_area_helper.map_areas
        self.map_area_display = self.map_area_helper.map_area_display

        self.full_enrollment_datetime = arrow.Arrow.fromdatetime(
            full_enrollment_datetime, full_enrollment_datetime.tzinfo).to(
                'utc').ceil('hour').datetime
        if full_enrollment_datetime:
            if not (self.start < self.full_enrollment_datetime <= self.end):
                start = self.start.strftime('%Y-%m-%d %Z')
                full = self.full_enrollment_datetime.strftime('%Y-%m-%d %Z')
                end = self.end.strftime('%Y-%m-%d %Z')
                raise SurveyError(
                    f'Invalid Survey. Full enrollment date must be within '
                    f'start and end dates. Got {start} < {full} <= {end} for '
                    f'survey \'{self.map_areas}\'.')

    def __repr__(self):
        start = self.start.strftime('%Y-%m-%d %Z')
        end = self.end.strftime('%Y-%m-%d %Z')
        return (f'{self.__class__.__name__}(\'{self.field_value}\', '
                f'{start}, {end})')

    def __str__(self):
        return self.field_value

    @property
    def field_value(self):
        """Returns the survey string stored in model instances with
        the `survey` field, e.g. household_structure.
        """
        return (f'{self.group_name}.{self.schedule_name}.'
                f'{self.name}.{self.map_area}')

    @property
    def short_name(self):
        return f'{self.schedule_name}.{self.name}'

    @property
    def long_name(self):
        """Alias for field_value.
        """
        return self.field_value

    def to_sparser(self):
        return S(self.field_value)

    @property
    def group_name(self):
        return self.survey_schedule.group_name

    @property
    def schedule_name(self):
        return self.survey_schedule.name

    @property
    def survey_schedule_name(self):
        """Alias for `schedule_name`.
        """
        return self.schedule_name

    @property
    def breadcrumbs(self):
        return [self.group_name, self.schedule_name, self.name]

    @property
    def previous(self):
        """Returns the previous current survey or None.
        """
        from .site_surveys import site_surveys
        return site_surveys.previous_survey(self)

    @property
    def next(self):
        """Returns the next current survey or None.
        """
        from .site_surveys import site_surveys
        return site_surveys.next_survey(self)
