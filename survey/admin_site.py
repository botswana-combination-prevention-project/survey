# coding=utf-8

from django.contrib.admin import AdminSite


class SurveyAdminSite(AdminSite):
    site_title = 'Survey'
    site_header = 'Survey'
    index_title = 'Survey'
    site_url = '/'
survey_admin = SurveyAdminSite(name='survey_admin')
