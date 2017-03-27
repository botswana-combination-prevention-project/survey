from django.apps import apps as django_apps
from django.db.models.constants import LOOKUP_SEP

from edc_device.constants import CLIENT, SERVER


class SurveyQuerysetViewMixin:

    survey_queryset_lookups = []

    @property
    def survey_lookup_prefix(self):
        survey_lookup_prefix = LOOKUP_SEP.join(self.survey_queryset_lookups)
        return '{}__'.format(survey_lookup_prefix) if survey_lookup_prefix else ''

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        edc_device_app_config = django_apps.get_app_config('edc_device')
        if edc_device_app_config.device_role in [SERVER, CLIENT]:
            options.update(
                {'{}survey_schedule'.format(self.survey_lookup_prefix):
                 self.survey_schedule_object.field_value})
        return options
