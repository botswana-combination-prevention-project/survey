# coding=utf-8

from survey.exceptions import SurveyScheduleError, AddSurveyDateError, AddSurveyMapAreaError, AddSurveyNameError,\
    AddSurveyOverlapError


class SurveySchedule:

    def __init__(self, name=None, group_name=None, start_date=None, end_date=None, map_areas=None):
        self.registry = []
        self.group_name = group_name  # e.g. ESS
        self.survey_groups = []
        self.map_areas = map_areas  # if none, except any map_area
        self.name = name  # e.g. year-1, year-2, ...
        self.start_date = start_date
        self.end_date = end_date
        if self.start_date > self.end_date:
            raise SurveyScheduleError('Invalid Survey schedule. Start date may not precede end date')
        if self.start_date == self.end_date:
            raise SurveyScheduleError('Invalid Survey schedule. Start date may not equal end date')

    def __repr__(self):
        return 'SurveySchedule(\'{0.label}\', {0.start_date}, {0.end_date})'.format(self)

    def __str__(self):
        return self.label

    @property
    def label(self):
        return '{}.{}'.format(self.group_name, self.name)

    @property
    def surveys(self):
        return self.registry

    def add_survey(self, *surveys):
        for survey in surveys:
            if not (self.start_date <= survey.start_date <= self.end_date):
                raise AddSurveyDateError(
                    'Unable to add survey to schedule {}. Survey {}.start_date is invalid. '
                    'Got {}.'.format(self.name, survey.name, self.start_date))
            if not (self.start_date <= survey.end_date <= self.end_date):
                raise AddSurveyDateError(
                    'Unable to add survey to schedule {}. Survey {}.end_date is invalid. '
                    'Got {}.'.format(self.name, survey.name, self.start_date))
            if survey.name in self.registry:
                raise AddSurveyNameError(
                    'Unable to add survey to schedule {}. A Survey with for map_area has already been '
                    'added. Got {}.'.format(self.name, survey.name))
            if survey.map_area in self.registry:
                raise AddSurveyMapAreaError(
                    'Unable to add survey to schedule {}. A Survey with for map_area has already been '
                    'added . Got {}.'.format(self.name, survey.name))
            if self.map_areas:
                if survey.map_area not in self.map_areas:
                    raise AddSurveyMapAreaError(
                        'Unable to add survey to schedule. Invalid map_area for scheudle {}. Got {}.'.format(
                            self.name, survey.map_area))
            if self.get_surveys(map_area=survey.map_area, reference_date=survey.start_date):
                raise AddSurveyOverlapError()
            survey.survey_schedule = self.label
            self.registry.append(survey)

    def get_surveys(self, map_area=None, reference_date=None):
        """Returns a list of surveys that meet the criteria."""
        def in_date_range(survey, reference_date):
            if survey.start_date <= reference_date <= survey.end_date:
                return True
            return False
        surveys = []
        if reference_date and map_area:
            surveys = [s for s in self.registry if s.map_area == map_area and in_date_range(s, reference_date)]
        elif map_area:
            surveys = [s for s in self.registry if s.map_area == map_area]
        elif reference_date:
            surveys = [s for s in self.registry if in_date_range(s, reference_date)]
        return surveys
