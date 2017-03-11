from django.db import models

from .site_surveys import site_surveys


class SurveyScheduleModelMixin(models.Model):

    survey_schedule = models.CharField(
        max_length=150,
        help_text="survey schedule name plus map_area")

    @property
    def survey_schedule_object(self):
        return site_surveys.get_survey_schedule_from_field_value(self.survey_schedule)

    class Meta:
        abstract = True


class SurveyModelMixin(SurveyScheduleModelMixin):

    survey = models.CharField(
        max_length=150)

    @property
    def survey_object(self):
        return site_surveys.get_survey_from_field_value(self.survey)

    class Meta:
        abstract = True
