from ..site_surveys import site_surveys
from .surveys import survey_one, survey_two, survey_three


class LoadTestSurveysError(Exception):
    pass


def load_test_surveys(load_count=None, load_all=None,
                      current_survey_index=None, register_current=None,
                      survey_schedules=None, group_name=None, constants=None):
    """Loads survey_schedules into site_surveys manually.
    """
    survey_schedules = (survey_schedules
                        or [survey_one, survey_two, survey_three])
    group_name = group_name or 'test_survey'
    if load_all:
        load_count = len(survey_schedules)
    elif not load_count:
        load_count = 1
    elif 0 < load_count > len(survey_schedules):
        raise LoadTestSurveysError(f'Invalid load count. Got {load_count}.')

    if not current_survey_index:
        current_survey_index = 0
    elif current_survey_index and 0 < current_survey_index > (len(survey_schedules) - 1):
        raise LoadTestSurveysError(
            f'Invalid current_survey_index. Got {current_survey_index}.')

    register_current = True if register_current is None else register_current

    for survey_schedule in survey_schedules:
        survey_schedule.group_name = group_name
        survey_schedule.current = False
        for survey in survey_schedule.surveys:
            survey.current = False
    site_surveys._registry = []
    site_surveys.loaded_current = False
    site_surveys.loaded = False
    site_surveys.current_survey_schedules = []
    site_surveys.current_surveys = []
    site_surveys.constants = constants or {}

    for index, survey_schedule in enumerate(survey_schedules):
        if index <= load_count - 1:
            site_surveys.register(survey_schedule)

    if register_current is True:
        # register the current survey schedule / surveys
        site_surveys.register_current(survey_schedules[current_survey_index])
