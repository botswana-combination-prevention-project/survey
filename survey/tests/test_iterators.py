# coding=utf-8

from django.test import TestCase, tag

from ..iterators import SurveyScheduleIterator
from ..site_surveys import site_surveys
from .models import HouseholdStructure, Household
from .survey_test_helper import SurveyTestHelper
from .surveys import survey_two, survey_three
from survey.tests.models import HouseholdMember
from uuid import uuid4
from survey.tests.surveys import survey_one


class TestIteratorWithHouseholdStructure(TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys(load_all=True)
        household = Household.objects.create()
        self.options = {'household': household}
        survey_schedules = site_surveys.get_survey_schedules(
            group_name='test_survey')
        self.obj1 = HouseholdStructure.objects.create(
            survey_schedule=survey_schedules[0].field_value, **self.options)
        self.obj2 = HouseholdStructure.objects.create(
            survey_schedule=survey_schedules[1].field_value, **self.options)
        self.obj3 = HouseholdStructure.objects.create(
            survey_schedule=survey_schedules[2].field_value, **self.options)

    @tag('1')
    def test_survey_schedule_iterator(self):
        survey_schedule_iterator = SurveyScheduleIterator(
            model_obj=self.obj1, **self.options)
        next_obj = next(survey_schedule_iterator)
        self.assertEqual(next_obj, self.obj2)
        next_obj = next(survey_schedule_iterator)
        self.assertEqual(next_obj, self.obj3)
        self.assertRaises(StopIteration, next, survey_schedule_iterator)

    @tag('1')
    def test_survey_schedule_as_list(self):
        survey_schedule_iterator = SurveyScheduleIterator(
            model_obj=self.obj1, **self.options)
        self.assertEqual(
            [obj.survey_schedule for obj in list(survey_schedule_iterator)],
            [survey_two.field_value, survey_three.field_value])

    @tag('1')
    def test_survey_schedule_iterator_reversed(self):
        survey_schedule_iterator = SurveyScheduleIterator(
            model_obj=self.obj1, **self.options)
        result = []
        for survey_schedule in reversed(list(survey_schedule_iterator)):
            result.append(survey_schedule)
        self.assertEqual([obj.survey_schedule for obj in result], [
                         survey_three.field_value, survey_two.field_value])


class TestIteratorWithHouseholdMember(TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys(load_all=True)
        household = Household.objects.create()
        survey_schedules = site_surveys.get_survey_schedules(
            group_name='test_survey')
        for survey_schedule in survey_schedules:
            HouseholdStructure.objects.create(
                survey_schedule=survey_schedule.field_value, household=household)
        self.internal_identifier = uuid4()
        for household_structure in HouseholdStructure.objects.all():
            HouseholdMember.objects.create(
                internal_identifier=self.internal_identifier,
                household_structure=household_structure)

    @tag('1')
    def test_survey_schedule_iterator_next(self):
        member1 = HouseholdMember.objects.get(
            survey_schedule=survey_one.field_value)
        member2 = HouseholdMember.objects.get(
            survey_schedule=survey_two.field_value)
        member3 = HouseholdMember.objects.get(
            survey_schedule=survey_three.field_value)
        survey_schedule_iterator = SurveyScheduleIterator(
            model_obj=member1, internal_identifier=self.internal_identifier)
        next_obj = next(survey_schedule_iterator)
        self.assertEqual(next_obj, member2)
        next_obj = next(survey_schedule_iterator)
        self.assertEqual(next_obj, member3)
        self.assertRaises(StopIteration, next, survey_schedule_iterator)

    @tag('1')
    def test_survey_schedule_iterator_previous(self):
        member1 = HouseholdMember.objects.get(
            survey_schedule=survey_one.field_value)
        member2 = HouseholdMember.objects.get(
            survey_schedule=survey_two.field_value)
        member3 = HouseholdMember.objects.get(
            survey_schedule=survey_three.field_value)
        survey_schedule_iterator = SurveyScheduleIterator(
            model_cls=HouseholdMember, internal_identifier=self.internal_identifier)
        iterable = reversed(survey_schedule_iterator)
        previous_obj = next(iterable)
        self.assertEqual(previous_obj, member3)
        next_obj = next(iterable)
        self.assertEqual(next_obj, member2)
        next_obj = next(iterable)
        self.assertEqual(next_obj, member1)
        self.assertRaises(StopIteration, next, iterable)

    @tag('1')
    def test_survey_schedule_iterator_previous2(self):
        member1 = HouseholdMember.objects.get(
            survey_schedule=survey_one.field_value)
        member2 = HouseholdMember.objects.get(
            survey_schedule=survey_two.field_value)
        member3 = HouseholdMember.objects.get(
            survey_schedule=survey_three.field_value)
        survey_schedule_iterator = SurveyScheduleIterator(
            model_obj=member1, internal_identifier=self.internal_identifier)
        iterable = reversed(survey_schedule_iterator)
        previous_obj = next(iterable)
        self.assertEqual(previous_obj, member3)
        next_obj = next(iterable)
        self.assertEqual(next_obj, member2)
        self.assertRaises(StopIteration, next, iterable)

    @tag('1')
    def test_survey_schedule_iterator_previous3(self):
        member1 = HouseholdMember.objects.get(
            survey_schedule=survey_one.field_value)
        member2 = HouseholdMember.objects.get(
            survey_schedule=survey_two.field_value)
        member3 = HouseholdMember.objects.get(
            survey_schedule=survey_three.field_value)
        member2.delete()
        survey_schedule_iterator = SurveyScheduleIterator(
            model_cls=HouseholdMember, internal_identifier=self.internal_identifier)
        iterable = reversed(survey_schedule_iterator)
        previous_obj = next(iterable)
        self.assertEqual(previous_obj, member3)
        previous_obj = next(iterable)
        self.assertEqual(previous_obj, member1)
        self.assertRaises(StopIteration, next, iterable)
