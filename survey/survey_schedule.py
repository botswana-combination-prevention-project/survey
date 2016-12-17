# coding=utf-8

from survey.exceptions import SurveyScheduleError


class SurveySchedule:

    def __init__(self, name=None, start_datetime=None, end_datetime=None):
        self.surveys = {}
        self.name = name
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        if self.start_datetime > self.end_datetime:
            raise SurveyScheduleError('Invalid Survey schedule. Start date may not precede end date')

    def __str__(self):
        return self.name

    def add_survey(self, survey):
        if survey.map_area not in self.surveys:
            self.surveys.update({survey.map_area: survey})
        else:
            raise SurveyScheduleError(
                'A Survey with for map_area has already been '
                'added to schedule {}. Got {}.'.format(self.name, survey.map_area))
