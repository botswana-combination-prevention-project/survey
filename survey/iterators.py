from .site_surveys import site_surveys


class SurveyScheduleIterator:

    """Iterates to the next survey schedule relative to the given
    survey schedule.
    """

    def __init__(self, survey_schedule=None):
        self.n = None
        self.survey_schedule = None
        self.initial = survey_schedule
        self.n = self.initial

    def __iter__(self):
        self.n = self.initial
        return self

    def __next__(self):
        self.n = site_surveys.next_survey_schedule(self.n)
        if not self.n:
            raise StopIteration
        return self.n
