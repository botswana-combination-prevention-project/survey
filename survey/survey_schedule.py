# coding=utf-8

from survey.exceptions import SurveyScheduleError
from edc_base.utils import get_utcnow


class SurveySchedule:

    def __init__(self, name=None, start_date=None, end_date=None):
        self.surveys = {}
        self.survey_groups = []
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        if self.start_date > self.end_date:
            raise SurveyScheduleError('Invalid Survey schedule. Start date may not precede end date')
        if self.start_date == self.end_date:
            raise SurveyScheduleError('Invalid Survey schedule. Start date may not equal end date')

    def __str__(self):
        return self.name

    def add_survey(self, survey):
        if not (self.start_date <= survey.start_date <= self.end_date):
            raise SurveyScheduleError(
                'Unable to add survey to schedule. Survey {}.start_date is invalid. '
                'Got {}.'.format(survey.map_area, self.start_date))
        if not (self.start_date <= survey.end_date <= self.end_date):
            raise SurveyScheduleError(
                'Unable to add survey to schedule. Survey {}.end_date is invalid. '
                'Got {}.'.format(survey.map_area, self.start_date))
        if survey.map_area in self.surveys:
            raise SurveyScheduleError(
                'Unable to add survey to schedule. A Survey with for map_area has already been '
                'added to schedule {}. Got {}.'.format(self.name, survey.map_area))
        self.surveys.update({survey.map_area: survey})
        if survey.group not in self.survey_groups:
            self.survey_groups.append(survey.group)

    def get_survey(self, reference_date=None, survey_group=None):
        reference_date = reference_date or get_utcnow.date()
        if survey_group:
            surveys = [s for s in self.surveys.values() if s.group == survey_group]
        else:
            surveys = self.surveys.values()
        for survey in surveys:
            if survey.start_date <= reference_date <= survey.end_date:
                get_survey = survey
        if not get_survey:
            raise SurveyScheduleError(
                'Unable to retrieve survey. Using survey_group={}, reference_date={}'.format(
                    survey_group, reference_date))
        return None
