# coding=utf-8

from survey.exceptions import SurveyError


class Survey:

    def __init__(self, map_area=None, start_datetime=None, end_datetime=None,
                 full_enrollment_datetime=None, **options):
        self.map_area = map_area
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.full_enrollment_datetime = full_enrollment_datetime
        if self.start_datetime >= self.end_datetime:
            raise SurveyError(
                'Invalid Survey. Start date may not precede or equal end date. Got {} > {} for survey \'{}\''.format(
                    self.start_datetime, self.end_datetime, self.map_area))
        if not (self.start_datetime < self.full_enrollment_datetime <= self.end_datetime):
            raise SurveyError(
                'Invalid Survey. Full enrollment date must be within start and end dates. '
                'Got {} < {} <= {} for survey \'{}\'.'.format(
                    self.start_datetime, self.full_enrollment_datetime, self.end_datetime, self.map_area))
        for key, value in options.items():
            try:
                getattr(self, key)
            except AttributeError:
                setattr(self, key, value)

    def __str__(self):
        return self.map_area
