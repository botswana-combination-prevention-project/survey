from django.apps import apps as django_apps
from django.db.models.constants import LOOKUP_SEP

from edc_device.constants import CLIENT, SERVER, NODE_SERVER


class SurveyQuerysetViewMixin:

    """Declare together with SurveyViewMixin and ListboardFilterViewMixin.
    """

    survey_queryset_lookups = []
    device_roles = [NODE_SERVER, SERVER, CLIENT]

    @property
    def survey_lookup_prefix(self):
        survey_lookup_prefix = LOOKUP_SEP.join(self.survey_queryset_lookups)
        return f'{survey_lookup_prefix}__' if survey_lookup_prefix else ''

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        if self.device_role in self.device_roles:
            options.update(
                {f'{self.survey_lookup_prefix}survey_schedule':
                 self.survey_schedule_object.field_value})
        return options

    @property
    def device_role(self):
        edc_device_app_config = django_apps.get_app_config('edc_device')
        return edc_device_app_config.device_role
