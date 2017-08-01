from django.db import models

from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow

from ..model_mixins import SurveyScheduleModelMixin, SurveyModelMixin


class Household(models.Model):

    report_datetime = models.DateTimeField(default=get_utcnow)


class HouseholdStructure(SurveyScheduleModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)

    household = models.ForeignKey(Household)


class HouseholdMember(SurveyScheduleModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)

    household_structure = models.ForeignKey(HouseholdStructure)

    internal_identifier = models.UUIDField()

    def save(self, *args, **kwargs):
        self.survey_schedule = self.household_structure.survey_schedule
        super().save(*args, **kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.survey_schedule})'


class SubjectVisit(SurveyModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)
