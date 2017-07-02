from django.conf import settings

if settings.APP_NAME == 'survey':
    from .tests.models import HouseholdStructure, SubjectVisit
