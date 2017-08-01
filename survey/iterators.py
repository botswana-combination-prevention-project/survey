from django.core.exceptions import ObjectDoesNotExist
from survey.site_surveys import site_surveys


class SurveyScheduleIterator:

    """Iterates to the next survey schedule relative to the
    given model object.

    If no model_obj given, will iterate over all.
    """

    def __init__(self, model_obj=None, model_cls=None, **options):
        self.n = 0
        if not model_cls:
            self.model_cls = model_obj.__class__
        else:
            self.model_cls = model_cls
        self.filter_options = options
        self.model_obj = model_obj
        self.first_model_object = model_obj

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        """Returns the next object or raises StopIteration.

        Skips over a None in the sequence, e.g. returns "3" in sequence
        1, None, 3.
        """
        if not self.model_obj and self.n == 0:
            for survey_schedule in site_surveys.get_survey_schedules():
                self.model_obj = self.model_cls.objects.get(
                    survey_schedule=survey_schedule,
                    **self.filter_options)
                if self.model_obj:
                    break
        elif self.model_obj:
            survey_schedule_object = self.model_obj.survey_schedule_object
            while True:
                survey_schedule_object = survey_schedule_object.next
                try:
                    self.model_obj = self.model_cls.objects.get(
                        survey_schedule=survey_schedule_object.field_value,
                        **self.filter_options)
                except ObjectDoesNotExist:
                    continue
                except AttributeError:
                    self.model_obj = None
                    break
                else:
                    break
        if not self.model_obj:
            raise StopIteration
        self.n += 1
        return self.model_obj

    def __reversed__(self):
        iterable = list(self)
        return reversed(iterable)
