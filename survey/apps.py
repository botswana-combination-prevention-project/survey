# coding=utf-8

import sys

from django.apps import AppConfig as DjangoApponfig
from django.core.management.color import color_style

from .site_surveys import site_surveys

style = color_style()


class AppConfig(DjangoApponfig):
    name = 'survey'
    current_survey = None

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_surveys.autodiscover()
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
