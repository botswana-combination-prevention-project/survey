from django.apps import AppConfig as DjangoApponfig


class AppConfig(DjangoApponfig):
    name = 'survey'
    current_survey = None
