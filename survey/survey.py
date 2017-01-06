# coding=utf-8
import arrow

from survey.exceptions import SurveyError


class Survey:

    def __init__(self, name=None, map_area=None, start=None, end=None,
                 full_enrollment_datetime=None, position=None):
        self.survey_schedule = None  # set when registered to a survey_schedule
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
        return '{}(\'{label}\', {start}, {end})'.format(
            self.__class__.__name__,
            self.label,
            self.start.strftime('%Y-%m-%d %Z'),
            self.end.strftime('%Y-%m-%d %Z'))

    def __str__(self):
        return self.label

    @property
    def label(self):
        return '{}.{}.{}'.format(self.survey_schedule, self.name, self.map_area)

    @property
    def short_name(self):
        return '{}.{}'.format(self.survey_schedule.split('.')[1], self.name.upper())

    @property
    def map_area_display(self):
        return ' '.join([word[0].upper() for word in self.map_area.split('_')])

    @property
    def rstart(self):
        return arrow.Arrow.fromdatetime(self.start, self.start.tzinfo).to('utc')

    @property
    def rend(self):
        return arrow.Arrow.fromdatetime(self.end, self.end.tzinfo).to('utc')
