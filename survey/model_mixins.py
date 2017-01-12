from django.db import models

from .site_surveys import site_surveys
from .sparser import S


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
        max_length=15,
        help_text="survey name, e.g. ESS, BHS, ...")

    @property
    def survey_object(self):
        s = S(self.survey_schedule, survey=self.survey)
        return site_surveys.get_survey_from_field_value(s.survey_field_value)

    class Meta:
        abstract = True
