# coding=utf-8

from django.core.exceptions import ValidationError
from survey.site_surveys import site_surveys


def date_in_survey(value):
    for survey_schedule_collection in site_surveys.get_survey_schedules():
        for survey_schedules in survey_schedule_collection.value():
            survey_schedules.get_surveys_by_date(value)
                
    survey = Survey.objects.current_survey()
    if survey:
        if survey.datetime_start <= value <= survey.datetime_end:
            # is in between start and end
            pass
        else:
            raise ValidationError('Date is not within the current survey. You entered {0}.'.format(value))
    else:
        raise ValidationError('Cannot determine the current survey. Have any surveys been defined?.')
