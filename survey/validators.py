# coding=utf-8

from django.core.exceptions import ValidationError
from survey.site_surveys import site_surveys


def date_in_survey_for_map_area(value):
    raise TypeError('validator not implemented')
#     for survey in site_surveys.surveys():
#
#     if (self.start_date <= survey.start_date <= self.end_date)            # is in between start and end
#             pass
#         else:
#             raise ValidationError('Date is not within the current survey. You entered {0}.'.format(value))
#     else:
#         raise ValidationError('Cannot determine the current survey. Have any surveys been defined?.')
