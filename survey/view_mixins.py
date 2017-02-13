from django.apps import apps as django_apps

from .site_surveys import site_surveys


class SurveyViewMixin:

    def get_context_data(self, **kwargs):
        """Add survey and survey_schedule objects to the context."""
        context = super().get_context_data(**kwargs)
        if self.survey_schedule_object:
            context.update(
                survey_schedule=self.survey_schedule_object.field_value,
                survey_schedule_object=self.survey_schedule_object,
                survey_schedules=self.survey_schedules,
                map_area=self.map_area)
        if self.survey_object:
            context.update(
                survey=self.survey_object.field_value,
                survey_object=self.survey_object)
        return context

    @property
    def map_area(self):
        try:
            map_area = self.survey_schedule_object.map_area_display
        except AttributeError:
            map_area = None
        return map_area

    @property
    def survey_object(self, **kwargs):
        return site_surveys.get_survey_from_field_value(
            self.kwargs.get('survey'))

    @property
    def survey_schedule_object(self):
        current_survey_schedule = django_apps.get_app_config(
            'survey').current_survey_schedule
        survey_schedule = self.kwargs.get(
            'survey_schedule', current_survey_schedule)
        return site_surveys.get_survey_schedule_from_field_value(
            survey_schedule)

    @property
    def survey_schedules(self):
        return site_surveys.get_survey_schedules(
            group_name=self.survey_schedule_object.group_name)
