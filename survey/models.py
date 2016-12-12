from datetime import datetime

from django.db import models
from django.template.defaultfilters import slugify

from edc_base.model.models import BaseUuidModel

from .managers import SurveyManager


class Survey (BaseUuidModel):

    survey_name = models.CharField(
        verbose_name="Survey name",
        max_length=15,
        unique=True,
    )

    survey_slug = models.SlugField(max_length=40)

    survey_description = models.CharField(
        verbose_name="Description",
        max_length=15,
        help_text="",
        null=True,
        blank=True,
    )

    chronological_order = models.IntegerField(default=0, db_index=True)

    datetime_start = models.DateTimeField(
        verbose_name="Start Date",
        help_text="",
    )

    datetime_end = models.DateTimeField(
        verbose_name="End Date",
        help_text="",
    )

    objects = SurveyManager()

    def natural_key(self):
        return (self.survey_slug, )

    def __str__(self):
        return self.survey_slug

    def save(self, *args, **kwargs):
        if not self.id:
            self.survey_slug = slugify(self.survey_name)
        super(Survey, self).save(*args, **kwargs)

    @property
    def not_started(self):
        return self.datetime_start > datetime.today()

    class Meta:
        app_label = 'survey'
        ordering = ['survey_name', ]
