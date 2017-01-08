from django.db import models

from survey.site_surveys import site_surveys


class SurveyModelMixin(models.Model):

    survey = models.CharField(max_length=75)

    @property
    def survey_object(self):
        return site_surveys.get_survey_from_field_value(self.survey)

    @property
    def survey_object(self):
        return site_surveys.get_survey_from_field_value(self.survey)

    class Meta:
        abstract = True
