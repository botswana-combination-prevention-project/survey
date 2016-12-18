from django.db import models


class SurveyModelMixin(models.Model):

    survey = models.CharField(max_length=75)

    def save(self, *args, **kwargs):
        """Restricts the concrete model from editing data outside of the start
        and full_enrollment dates for the current survey."""

        # maybe have this as a method used by others to check if survey data may be edited
#                 if app_config.enrollment.status == CLOSED:
#                     mapper_instance = site_mappers.get_mapper(site_mappers.current_map_area)
#                     if self.report_datetime > pytz.utc.localize(
#                             mapper_instance.current_survey_dates.full_enrollment_date):
#                         raise PlotEnrollmentError(
#                             'Enrollment for {0} ended on {1}. This plot, and the '
#                             'data related to it, may not be modified. '
#                             'See site_mappers'.format(
#                                 self.community,
#                                 mapper_instance.current_survey_dates.full_enrollment_date.strftime('%Y-%m-%d')))
        super().save(*args, **kwargs)

    @property
    def survey_label(self):
        return self.survey

    class Meta:
        abstract = True
