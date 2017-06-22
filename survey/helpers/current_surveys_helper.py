from django.core.exceptions import ValidationError


class CurrentSurveyError(ValidationError):
    pass


class CurrentSurveysHelper:

    def __init__(self, current_survey_schedules=None, registered_survey_schedules=None):
        self.current_survey_schedules = []
        self.current_surveys = []
        self.registered_survey_schedules = {}

        for survey_schedule in registered_survey_schedules:
            self.registered_survey_schedules.update(
                {survey_schedule.field_value: survey_schedule})

        try:
            current_sparsers = []
            for survey_schedule in current_survey_schedules:
                current_sparsers.extend(survey_schedule.to_sparsers())
        except AttributeError as e:
            if 'to_sparsers' not in str(e):
                raise AttributeError(e)
            current_sparsers = current_survey_schedules

        for sparser in current_sparsers:
            registered_survey_schedule = self.registered_survey_schedules.get(
                sparser.survey_schedule_field_value)
            try:
                survey_names = [
                    s.survey_name for s in registered_survey_schedule.surveys]
            except AttributeError:
                raise CurrentSurveyError(
                    f'Survey schedule is not registered. Got {sparser}',
                    code='not_found')
            else:
                if sparser.survey_name not in survey_names:
                    raise CurrentSurveyError(
                        f'Survey schedule contains a survey that is not '
                        f'registered. Got {sparser}',
                        code='survey_name')
            registered_survey_schedule.current = True
            self.current_survey_schedules.append(registered_survey_schedule)

        for survey_schedule in self.current_survey_schedules:
            for survey in survey_schedule.surveys:
                if survey.long_name in [s.name for s in current_sparsers]:
                    survey.current = True
                    self.current_surveys.append(survey)

        self.current_surveys = list(set(self.current_surveys))
        self.current_surveys.sort(key=lambda x: x.start)
