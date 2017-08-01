from django.db import models

from .site_surveys import site_surveys


class SurveyScheduleModelMixin(models.Model):
    """Access survey schedule attrs via a model.

    Note: the model must set the survey_schedule field manually.
    For example, see post_save signal in household that creates
    HouseholdStructure instances.
    """

    survey_schedule = models.CharField(
        max_length=150,
        help_text='survey_schedule.field_value')

    @property
    def survey_schedule_object(self):
        return site_surveys.get_survey_schedule_from_field_value(
            self.survey_schedule)

    class Meta:
        abstract = True


class SurveyModelMixin(SurveyScheduleModelMixin):
    """Access survey attrs via a model.

    Note: the model must set the survey field manually.
    For example, see save methods on visit or CRFs.
    """

    survey = models.CharField(
        max_length=150,
        help_text='survey.field_value')

    @property
    def survey_object(self):
        return site_surveys.get_survey_from_field_value(self.survey)

    class Meta:
        abstract = True
