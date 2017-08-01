import re

from .patterns import survey as survey_pattern
from .patterns import survey_schedule as survey_schedule_pattern


class SurveyParserError(Exception):
    pass


class S:
    """A simple class to parse survey / survey schedule name.

    Makes no attempt to validate the values.

    format is S('group.survey_schedule.survey.map_area', **kwargs)
    """

    def __init__(self, s, survey_name=None, inactive=None, ):
        self._s = s
        self.survey_name = None
        if re.match(survey_pattern, s or ''):
            (self.group_name, self.survey_schedule_name,
             self.survey_name, self.map_area) = s.split('.')
        elif re.match(survey_schedule_pattern, s or ''):
            (self.group_name, self.survey_schedule_name,
             self.map_area) = s.split('.')
            self.survey_name = survey_name
            if not self.survey_name:
                raise SurveyParserError(
                    f'Missing required survey_name. Got {repr(self)}.')
        else:
            raise SurveyParserError(f'Invalid format. Got {repr(self)}.')
        self.field_value = s
        self.inactive = inactive

    def __repr__(self):
        return f'{self.__class__.__name__}(\'{self._s}\', survey_name={self.survey_name})'

    def __str__(self):
        name = 'survey_schedule' if self.survey_schedule_field_value else 'survey'
        return f'{self.field_value} ({name})'

    @property
    def name(self):
        return self.field_value

    @property
    def survey_field_value(self):
        return (f'{self.group_name}.{self.survey_schedule_name}.'
                f'{self.survey_name}.{self.map_area}')

    @property
    def survey_schedule_field_value(self):
        return f'{self.group_name}.{self.survey_schedule_name}.{self.map_area}'
