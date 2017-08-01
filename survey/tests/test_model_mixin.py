from django.test import TestCase

from ..site_surveys import site_surveys
from .models import HouseholdStructure, SubjectVisit
from .survey_test_helper import SurveyTestHelper
from survey.tests.models import Household


class TestModelMixin(TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        # Note: this code is in a post_save signal in module household
        household = Household.objects.create()
        for survey_schedule in site_surveys.get_survey_schedules(current=True):
            try:
                HouseholdStructure.objects.get(
                    household=household,
                    survey_schedule=survey_schedule.field_value)
            except HouseholdStructure.DoesNotExist:
                HouseholdStructure.objects.create(
                    household=household,
                    survey_schedule=survey_schedule.field_value)

    def test_models_field(self):
        """Asserts  object.field value set the model field
        correctly.
        """
        self.assertEqual(HouseholdStructure.objects.all().count(), 1)
        for obj in HouseholdStructure.objects.all():
            self.assertEqual(
                obj.survey_schedule,
                'test_survey.year-1.test_community')

    def test_model_survey_schedule_object(self):
        """Asserts survey_schedule_object attrs accessed via the
        model mixin.
        """
        for obj in HouseholdStructure.objects.all():
            self.assertEqual(
                obj.survey_schedule_object.group_name, 'test_survey')
            self.assertEqual(
                obj.survey_schedule_object.name, 'year-1')
            self.assertEqual(
                obj.survey_schedule_object.map_area, 'test_community')

    def test_model_survey_object(self):
        """Asserts survey_object attrs accessed via the
        model mixin.
        """
        for obj in HouseholdStructure.objects.all():
            survey_schedule = site_surveys.get_survey_schedule_from_field_value(
                obj.survey_schedule)
            for survey in survey_schedule.current_surveys:
                SubjectVisit.objects.create(survey=survey.field_value)
        for survey in survey_schedule.current_surveys:
            obj = SubjectVisit.objects.get(survey=survey.field_value)
            self.assertEqual(
                obj.survey_object.survey_schedule.field_value,
                'test_survey.year-1.test_community')
