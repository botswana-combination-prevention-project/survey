from ..site_surveys import site_surveys
from .surveys import survey_one, survey_two, survey_three


class LoadTestSurveysError(Exception):
    pass


def load_test_surveys(load_count=None, load_all=None,
                      current_survey_index=None, no_current=None):
    """Load surveys into site_surveys manually.
    """

    if load_all:
        load_count = 3
    elif not load_count:
        load_count = 1
    elif 0 < load_count > 3:
        raise LoadTestSurveysError(f'Invalid load count. Got {load_count}.')

    if not current_survey_index:
        current_survey_index = 0
    elif current_survey_index and 0 < current_survey_index > 2:
        raise LoadTestSurveysError(
            f'Invalid current_survey_index. Got {current_survey_index}.')

    if site_surveys.loaded:
        for survey_schedules in site_surveys.get_survey_schedules(current=True):
            survey_schedules.group_name = 'test_survey'
            for survey in survey_schedules.surveys:
                survey.current = False
    site_surveys._registry = []
    site_surveys.loaded_current = False
    site_surveys.loaded = False

    survey_schedules = [survey_one, survey_two, survey_three]

    for index, survey_schedule in enumerate(
            [survey_one, survey_two, survey_three]):
        if index <= load_count - 1:
            site_surveys.register(survey_schedule)

    if not no_current:
        # register the current survey schedule / surveys
        site_surveys.register_current(survey_schedules[current_survey_index])
