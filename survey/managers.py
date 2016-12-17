# coding=utf-8

from datetime import date

from django.apps import apps as django_apps
from django.db import models
from django.core.exceptions import MultipleObjectsReturned, ImproperlyConfigured
from django.conf import settings

app_config = django_apps.get_app_config('survey')


class SurveyManager(models.Manager):

    def get_by_natural_key(self, survey_name):
        return self.get(survey_name=survey_name)

    @property
    def first_survey(self):
        return self.all().order_by('datetime_start')[0]

    @property
    def last_survey(self):
        return self.all().order_by('-datetime_start')[0]

    def previous_survey(self, survey_slug=None):
        previous_survey = None
        current_survey_slug = survey_slug or settings.CURRENT_SURVEY
        try:
            previous_survey = self.exclude(survey_slug=current_survey_slug).order_by('datetime_start')[0]
        except IndexError:
            pass
        return previous_survey

    def next_survey(self, survey_slug=None):
        next_survey = None
        current_survey_slug = survey_slug or settings.CURRENT_SURVEY
        try:
            next_survey = self.exclude(survey_slug=current_survey_slug).order_by('-datetime_start')[0]
        except IndexError:
            pass
        return next_survey

    def current_survey(self, report_datetime=None, survey_slug=None, datetime_label=None, community=None):
        """Returns a survey instance or None.

        The return value may be:
        * the current survey based on today's date and the
          settings attribute CURRENT_SURVEY;
        * a survey relative to the given report_datetime and survey_slug;
        * None if both survey_slug and settings.CURRENT are None."""
        survey = None
        if app_config.current_survey:
            try:
                report_date = report_datetime.date() or date.today()
            except AttributeError:
                report_date = report_datetime or date.today()
            survey_slug = survey_slug or settings.CURRENT_SURVEY
            datetime_label = datetime_label or 'report_datetime'
            try:
                survey = self.get(
                    datetime_start__lte=report_date,
                    datetime_end__gte=report_date)
                if survey_slug:
                    survey = self.get(
                        datetime_start__lte=report_date,
                        datetime_end__gte=report_date,
                        survey_slug=survey_slug)
            except MultipleObjectsReturned:
                raise ImproperlyConfigured('Date {} falls within more than one Survey. Start and end dates'
                                           'may not overlap between Surveys. ({}). See app configuration.'.format(
                                               report_date, community))
            except self.model.DoesNotExist:
                if settings.ALLOW_ENROLLMENT:
                    raise ImproperlyConfigured(
                        'Expected survey \'{0}\'. {2} {1} does not fall within '
                        'the start/end dates of Survey \'{0}\' ({3}). See app_configuration or reload urls.'.format(
                            survey_slug,
                            report_date.strftime('%Y-%m-%d'),
                            '{}{}'.format(datetime_label[0].upper(), datetime_label[1:]),
                            community,
                        )
                    )
                else:
                    if survey_slug:
                        survey = self.get(survey_slug=survey_slug)
        return survey
