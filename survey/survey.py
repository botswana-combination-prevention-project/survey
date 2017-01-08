# coding=utf-8
import arrow

from survey.exceptions import SurveyError


class DummySurvey:
    survey_breadcrumbs = []
    map_area_display = None
    short_name = None
    field_value = None


class S:
    def __init__(self, s, inactive=None):
        self.group_name, self.survey_schedule_name, self.survey_name, self.map_area = s.split('.')
        self.field_value = s
        self.inactive = inactive

    def __str__(self):
        return '{}{}'.format(self.field_value, '' if not self.inactive else ' - inactive')

    @property
    def name(self):
        return self.field_value


class Survey:

    def __init__(self, name=None, map_area=None, start=None, end=None,
                 full_enrollment_datetime=None, position=None):
        self.survey_schedule = None  # set when registered to a survey_schedule
        self.current = False
        self.name = name
        self.position = position
        self.map_area = map_area
        self.start = arrow.Arrow.fromdatetime(start, start.tzinfo).to('utc').floor('hour').datetime
        self.end = arrow.Arrow.fromdatetime(end, end.tzinfo).to('utc').ceil('hour').datetime
        self.full_enrollment_datetime = arrow.Arrow.fromdatetime(
            full_enrollment_datetime, full_enrollment_datetime.tzinfo).to('utc').ceil('hour').datetime
        if self.start >= self.end:
            raise SurveyError(
                'Invalid Survey. Start date may not precede or equal end '
                'date. Got {} > {} for survey \'{}\''.format(
                    self.start.strftime('%Y-%m-%d %Z'), self.end.strftime('%Y-%m-%d %Z'), self.map_area))
        if full_enrollment_datetime:
            if not (self.start < self.full_enrollment_datetime <= self.end):
                raise SurveyError(
                    'Invalid Survey. Full enrollment date must be within start and end dates. '
                    'Got {} < {} <= {} for survey \'{}\'.'.format(
                        self.start.strftime('%Y-%m-%d %Z'),
                        self.full_enrollment_datetime.strftime('%Y-%m-%d %Z'),
                        self.end.strftime('%Y-%m-%d %Z'),
                        self.map_area))

    def __repr__(self):
        return '{}(\'{}\', {}, {})'.format(
            self.__class__.__name__,
            self.label,
            self.start.strftime('%Y-%m-%d %Z'),
            self.end.strftime('%Y-%m-%d %Z'))

    def __str__(self):
        return self.long_name

    @property
    def short_name(self):
        return '{}.{}'.format(self.survey_schedule.name, self.name.upper())

    @property
    def long_name(self):
        """Returns the survey string stored in model instances with
        the `survey` field, e.g. household_structure."""
        return '{}.{}.{}.{}'.format(
            self.survey_schedule.group_name, self.survey_schedule.name, self.name, self.map_area)

    @property
    def field_value(self):
        """Convenience method for models."""
        return self.long_name

    @property
    def group_name(self):
        return self.survey_schedule.group_name

    @property
    def schedule_name(self):
        return self.survey_schedule.name

    @property
    def map_area_display(self):
        return ' '.join([word[0].upper() for word in self.map_area.split('_')])

    @property
    def rstart(self):
        return arrow.Arrow.fromdatetime(self.start, self.start.tzinfo).to('utc')

    @property
    def rend(self):
        return arrow.Arrow.fromdatetime(self.end, self.end.tzinfo).to('utc')

    @property
    def previous(self):
        """Returns the previous current survey or None."""
        from .site_surveys import site_surveys
        return site_surveys.previous(self)

    @property
    def next(self):
        """Returns the next current survey or None."""
        from .site_surveys import site_surveys
        return site_surveys.next(self)

    @property
    def breadcrumbs(self):
        return [self.group_name, self.schedule_name, self.name]
