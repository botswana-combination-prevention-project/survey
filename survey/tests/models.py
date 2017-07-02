from django.db import models

from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow

from ..model_mixins import SurveyScheduleModelMixin, SurveyModelMixin


class HouseholdStructure(SurveyScheduleModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)


class SubjectVisit(SurveyModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)
