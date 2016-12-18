# coding=utf-8

from survey.exceptions import SurveyError


class Survey:

    def __init__(self, name=None, map_area=None, start_date=None, end_date=None,
                 full_enrollment_date=None):
        self.survey_schedule = None  # set when registered to a survey_schedule
        self.name = name
        self.map_area = map_area
        self.start_date = start_date
        self.end_date = end_date
        self.full_enrollment_date = full_enrollment_date
        if self.start_date >= self.end_date:
            raise SurveyError(
                'Invalid Survey. Start date may not precede or equal end date. Got {} > {} for survey \'{}\''.format(
                    self.start_date, self.end_date, self.map_area))
        if full_enrollment_date:
            if not (self.start_date < self.full_enrollment_date <= self.end_date):
                raise SurveyError(
                    'Invalid Survey. Full enrollment date must be within start and end dates. '
                    'Got {} < {} <= {} for survey \'{}\'.'.format(
                        self.start_date, self.full_enrollment_date, self.end_date, self.map_area))

    def __repr__(self):
        return 'Survey(\'{0.label}\', {0.start_date}, {0.end_date})'.format(self)

    def __str__(self):
        return self.label

    @property
    def label(self):
        return '{}.{}.{}'.format(self.survey_schedule, self.name, self.map_area)
