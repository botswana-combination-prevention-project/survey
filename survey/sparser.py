import re

from .exceptions import SurveyError
from .patterns import survey as survey_pattern, survey_schedule as survey_schedule_pattern


class S:
    """A simple class to parse survey / survey schedule name.

    Makes no attempt to validate the values."""

    def __init__(self, s, survey_name=None, inactive=None, ):
        self._s = s
        if re.match(survey_pattern, s):
            try:
                (self.group_name, self.survey_schedule_name,
                 self.survey_name, self.map_area) = s.split('.')
            except ValueError as e:
                raise SurveyError(f'{e} Got {s}')
        elif re.match(survey_schedule_pattern, s):
            try:
                self.group_name, self.survey_schedule_name, self.map_area = s.split(
                    '.')
            except ValueError as e:
                raise SurveyError('{} Got {}'.format(str(e), s))
            else:
                self.survey_name = survey_name
        else:
            raise SurveyError(f'Invalid survey name format. Got {s}.')
        self.field_value = s
        self.inactive = inactive

    def __repr__(self):
        return f'{self.__class__.__name__}(\'{self._s}\')'

    def __str__(self):
        name = 'survey_schedule' if self.survey_schedule_field_value else 'survey'
        return f'{self.field_value} ({name})'

    @property
    def name(self):
        return self.field_value

    @property
    def survey_field_value(self):
        if self.survey_name:
            return '{}.{}.{}.{}'.format(
                self.group_name, self.survey_schedule_name,
                self.survey_name, self.map_area)
        else:
            return None

    @property
    def survey_schedule_field_value(self):
        return f'{self.group_name}.{self.survey_schedule_name}.{self.map_area}'
