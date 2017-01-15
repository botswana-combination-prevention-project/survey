from django.apps import apps as django_apps

from .site_surveys import site_surveys


class SurveyViewMixin:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.survey_object = None
        self.survey_schedule_object = None
        self.survey_schedules = None

    def get(self, request, *args, **kwargs):
        """Add survey and survey_schedule objects to the instance."""

        self.survey_schedule_object = self.get_survey_schedule_object(**kwargs)
        if self.survey_schedule_object:
            kwargs['survey_schedule'] = self.survey_schedule_object.field_value
            kwargs['survey_schedule_object'] = self.survey_schedule_object

        if self.survey_schedule_object:
            self.survey_schedules = site_surveys.get_survey_schedules(
                group_name=self.survey_schedule_object.group_name)
            kwargs['survey_schedules'] = self.survey_schedules

        self.survey_object = self.get_survey_object(**kwargs)
        if self.survey_object:
            kwargs['survey'] = self.survey_object.field_value
            kwargs['survey_object'] = self.survey_object
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            map_area = self.survey_schedule_object.map_area_display
        except AttributeError:
            map_area = None
        context.update(map_area=map_area)
        return context

    def get_survey_object(self, **kwargs):
        survey = kwargs.get('survey')
        survey_object = site_surveys.get_survey_from_field_value(survey)
        return survey_object

    def get_survey_schedule_object(self, **kwargs):
        current_survey_schedule = django_apps.get_app_config('survey').current_survey_schedule
        survey_schedule = kwargs.get('survey_schedule', current_survey_schedule)
        survey_schedule_object = site_surveys.get_survey_schedule_from_field_value(
            survey_schedule)
        return survey_schedule_object
