# coding=utf-8

import sys

if 'test' in sys.argv:

    from dateutil.relativedelta import relativedelta

    from edc_base.utils import get_utcnow

    from .site_surveys import site_surveys
    from .survey import Survey
    from .survey_schedule import SurveySchedule

    current_map_area = 'test_community'
    map_areas = ['test_community']

    survey_one = SurveySchedule(
        name='year-1',
        group_name='test_survey',
        map_area=current_map_area,
        map_areas=map_areas,
        start=(get_utcnow() - relativedelta(years=3)),
        end=(get_utcnow() - relativedelta(years=2)))

    survey_two = SurveySchedule(
        name='year-2',
        group_name='test_survey',
        map_area=current_map_area,
        map_areas=map_areas,
        start=(get_utcnow() - relativedelta(years=2)),
        end=(get_utcnow() - relativedelta(years=1)))

    survey_three = SurveySchedule(
        name='year-3',
        group_name='test_survey',
        map_area=current_map_area,
        map_areas=map_areas,
        start=(get_utcnow() - relativedelta(years=1)),
        end=get_utcnow())

    baseline = Survey(
        name='baseline',
        position=0,
        map_area='test_community',
        start=(get_utcnow() - relativedelta(years=3)),
        end=(get_utcnow() - relativedelta(years=2)),
        full_enrollment_datetime=(get_utcnow() - relativedelta(years=2))
    )

    annual_1 = Survey(
        name='annual-1',
        position=1,
        map_area='test_community',
        start=(get_utcnow() - relativedelta(years=3)),
        end=(get_utcnow() - relativedelta(years=2)),
        full_enrollment_datetime=(get_utcnow() - relativedelta(years=2))
    )

    annual_2 = Survey(
        name='annual-2',
        position=2,
        map_area='test_community',
        start=(get_utcnow() - relativedelta(years=3)),
        end=(get_utcnow() - relativedelta(years=2)),
        full_enrollment_datetime=(get_utcnow() - relativedelta(years=2))
    )

    survey_one.add_survey(baseline, annual_1, annual_2)

    site_surveys.register(survey_one)
    # site_surveys.register(survey_two)
    # site_surveys.register(survey_three)
