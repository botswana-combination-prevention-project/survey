from django.core.exceptions import ValidationError

from .models import Survey


def date_in_survey(value):
    survey = Survey.objects.current_survey()
    if survey:
        if survey.datetime_start <= value <= survey.datetime_end:
            # is in between start and end
            pass
        else:
            raise ValidationError('Date is not within the current survey. You entered {0}.'.format(value))
    else:
        raise ValidationError('Cannot determine the current survey. Have any surveys been defined?.')
