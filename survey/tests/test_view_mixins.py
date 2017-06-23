from django.apps import apps as django_apps
from django.test import TestCase
from django.test.utils import override_settings
from django.views.generic.base import ContextMixin

from edc_device import CLIENT

from ..view_mixins import SurveyViewMixin, SurveyQuerysetViewMixin
from .survey_test_helper import SurveyTestHelper
from .surveys import survey_one


class TestView(SurveyViewMixin, ContextMixin):
    pass


class ListboardFilterViewMixin(ContextMixin):
    def get_queryset_filter_options(self, request, *args, **kwargs):
        return {}


class TestViewQs(SurveyViewMixin, SurveyQuerysetViewMixin,
                 ListboardFilterViewMixin, ContextMixin):
    pass


class TestSurveyViewMixin(TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys(load_all=True)
        self.view = TestView()

    def test_survey_schedule_object(self):
        self.view.kwargs = {
            'survey_schedule': 'test_survey.year-1'}
        self.assertIn('survey_schedule_object', self.view.get_context_data())
        context_data = self.view.get_context_data()
        self.assertEqual(
            survey_one, context_data.get('survey_schedule_object'))

    def test_survey_object(self):
        self.view.kwargs = {
            'survey_schedule': 'test_survey.year-1',
            'survey': 'test_survey.year-1.baseline.test_community'}
        self.assertIn('survey_object', self.view.get_context_data())
        context_data = self.view.get_context_data()
        self.assertEqual(
            survey_one.surveys[0], context_data.get('survey_object'))

    def test_survey_object_no_schedule(self):
        self.view.kwargs = {
            'survey': 'test_survey.year-1.baseline.test_community'}
        self.assertIn('survey_object', self.view.get_context_data())
        context_data = self.view.get_context_data()
        self.assertEqual(
            survey_one.surveys[0], context_data.get('survey_object'))

    def test_map_area_no_schedule(self):
        """Asserts determines survey_schedule from appconfig.
        """
        self.view.kwargs = {}
        context_data = self.view.get_context_data()
        self.assertIsNotNone(context_data.get('map_area'))


class TestSurveyQuerysetViewMixin(TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys(load_all=True)
        self.view = TestViewQs()

    def test_options(self):
        with override_settings(DEVICE_ID='10', DEVICE_ROLE=CLIENT):
            app_config = django_apps.get_app_config('edc_device')
            app_config.device_id = None
            app_config.messages_written = True
            app_config.ready()
            self.assertEqual(self.view.device_role, CLIENT)
            self.view.kwargs = {}
            options = self.view.get_queryset_filter_options(None, )
            self.assertIn('survey_schedule', options)

    def test_options2(self):
        with override_settings(DEVICE_ID='10', DEVICE_ROLE=CLIENT):
            app_config = django_apps.get_app_config('edc_device')
            app_config.device_id = None
            app_config.messages_written = True
            app_config.ready()
            self.assertEqual(self.view.device_role, CLIENT)
            self.view.survey_queryset_lookups = ['household']
            self.view.kwargs = {}
            options = self.view.get_queryset_filter_options(None, )
            self.assertIn('household__survey_schedule', options)

    def test_options3(self):
        with override_settings(DEVICE_ID='10', DEVICE_ROLE=CLIENT):
            app_config = django_apps.get_app_config('edc_device')
            app_config.device_id = None
            app_config.messages_written = True
            app_config.ready()
            self.assertEqual(self.view.device_role, CLIENT)
            self.view.survey_queryset_lookups = ['plot', 'household']
            self.view.kwargs = {}
            options = self.view.get_queryset_filter_options(None, )
            self.assertIn('plot__household__survey_schedule', options)
