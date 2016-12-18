# coding=utf-8

from survey.exceptions import SurveyScheduleError, AddSurveyDateError, AddSurveyMapAreaError, AddSurveyNameError,\
    AddSurveyOverlapError


class SurveySchedule:

    def __init__(self, name=None, start_date=None, end_date=None, map_areas=None):
        self.registry = {None: {}}
        self.survey_groups = []
        self.map_areas = map_areas  # if none, except any map_area
        self.name = name  # e.g. year-1, year-2, ...
        self.start_date = start_date
        self.end_date = end_date
        if self.start_date > self.end_date:
            raise SurveyScheduleError('Invalid Survey schedule. Start date may not precede end date')
        if self.start_date == self.end_date:
            raise SurveyScheduleError('Invalid Survey schedule. Start date may not equal end date')

    def __str__(self):
        return self.name

    def add_survey(self, *surveys):
        for survey in surveys:
            if not (self.start_date <= survey.start_date <= self.end_date):
                raise AddSurveyDateError(
                    'Unable to add survey to schedule. Survey {}.start_date is invalid. '
                    'Got {}.'.format(survey.map_area, self.start_date))
            if not (self.start_date <= survey.end_date <= self.end_date):
                raise AddSurveyDateError(
                    'Unable to add survey to schedule. Survey {}.end_date is invalid. '
                    'Got {}.'.format(survey.map_area, self.start_date))
            if survey.name in self.registry:
                raise AddSurveyNameError(
                    'Unable to add survey to schedule. A Survey with for map_area has already been '
                    'added to schedule {}. Got {}.'.format(self.name, survey.map_area))
            if survey.map_area in self.registry:
                raise AddSurveyMapAreaError(
                    'Unable to add survey to schedule. A Survey with for map_area has already been '
                    'added to schedule {}. Got {}.'.format(self.name, survey.map_area))
            if self.map_areas:
                if survey.map_area not in self.map_areas:
                    raise AddSurveyMapAreaError(
                        'Unable to add survey to schedule. Invalid map_area for scheudle {}. Got {}.'.format(
                            self.name, survey.map_area))
            objs = self.get_surveys_by_map_area(map_area=survey.map_area, survey_group=survey.group)
            if self.get_surveys_by_date(reference_date=survey.start_date, surveys=objs):
                raise AddSurveyOverlapError()
            if survey.group not in self.survey_groups:
                self.survey_groups.append(survey.group)
            surveys = self.registry.get(survey.group, {})
            surveys.update({survey.name: survey})
            self.registry.update({survey.group: surveys})

    def get_surveys(self, map_area=None, reference_date=None, survey_group=None):
        surveys = []
        if map_area:
            surveys = self.get_surveys_by_map_area(map_area, survey_group)
        if reference_date:
            surveys = self.get_surveys_by_date(reference_date, survey_group=survey_group, surveys=surveys)
        if not surveys:
            raise SurveyScheduleError(
                'Unable to retrieve survey. Using map_area={}, survey_group={}, reference_date={}'.format(
                    map_area, survey_group, reference_date))
        return surveys

    def get_surveys_by_date(self, reference_date, surveys=None, survey_group=None):
        objs = []
        if reference_date:
            if not surveys:
                surveys = [s for s in self.registry[survey_group].values()]
            for survey in surveys:
                if survey.start_date <= reference_date <= survey.end_date:
                    objs.append(survey)
        return objs

    def get_surveys_by_map_area(self, map_area, survey_group=None):
        objs = []
        try:
            surveys = [s for s in self.registry[survey_group].values()]
        except KeyError:
            surveys = []
        for survey in surveys:
            if survey.map_area == map_area:
                objs.append(survey)
        return objs
