from django.apps import apps as django_apps

from ..site_surveys import site_surveys
from .surveys import survey_one, survey_two, survey_three


class LoadTestSurveysError(Exception):
    pass


def load_test_surveys(current_surveys=None, load_count=None, load_all=None, current_survey_index=None):
    """Load surveys into site_surveys manually.

    Usage:"""

    if load_all:
        load_count = 3
    elif not load_count:
        load_count = 1
    elif 0 < load_count > 3:
        raise LoadTestSurveysError(f'Invalid load count. Got {load_count}.')

    if not current_survey_index:
        current_survey_index = 0
    elif 0 < current_survey_index > 2:
        raise LoadTestSurveysError(
            f'Invalid current_survey_index. Got {current_survey_index}.')

    if not current_surveys:
        app_config = django_apps.get_app_config('survey')
        current_surveys = app_config.current_surveys

    site_surveys._registry = []
    site_surveys.loaded_current = False
    site_surveys.loaded = False
    site_surveys.current_surveys = []

    survey_list = [survey_one, survey_two, survey_three]

    for index, survey in enumerate([survey_one, survey_two, survey_three]):
        if index <= load_count - 1:
            site_surveys.register(survey)

    site_surveys.register_current(*survey_list[current_survey_index])
