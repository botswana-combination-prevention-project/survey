# coding=utf-8

from survey.exceptions import SurveyError


class Survey:

    def __init__(self, map_area=None, group=None, start_date=None, end_date=None,
                 full_enrollment_date=None, **options):
        self.map_area = map_area
        self.group = group
        self.start_date = start_date
        self.end_date = end_date
        self.full_enrollment_date = full_enrollment_date
        if self.start_date >= self.end_date:
            raise SurveyError(
                'Invalid Survey. Start date may not precede or equal end date. Got {} > {} for survey \'{}\''.format(
                    self.start_date, self.end_date, self.map_area))
        if not (self.start_date < self.full_enrollment_date <= self.end_date):
            raise SurveyError(
                'Invalid Survey. Full enrollment date must be within start and end dates. '
                'Got {} < {} <= {} for survey \'{}\'.'.format(
                    self.start_date, self.full_enrollment_date, self.end_date, self.map_area))
        for key, value in options.items():
            try:
                getattr(self, key)
            except AttributeError:
                setattr(self, key, value)

    def __str__(self):
        return self.map_area
