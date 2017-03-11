import arrow

from ..exceptions import SurveyDateError


class DateMixin:

    def __init__(self, start=None, end=None, **kwargs):
        super().__init__(**kwargs)
        self.start = arrow.Arrow.fromdatetime(
            start, start.tzinfo).to('utc').floor('hour').datetime
        self.end = arrow.Arrow.fromdatetime(
            end, end.tzinfo).to('utc').ceil('hour').datetime

        if self.start > self.end:
            raise SurveyDateError(
                'Invalid {} date range. Start date may not precede end '
                'date. Got {} > {} for \'{}\''.format(
                    self.__class__.__name__,
                    self.start.strftime('%Y-%m-%d %Z'),
                    self.end.strftime('%Y-%m-%d %Z'),
                    self.name))

        if self.start == self.end:
            raise SurveyDateError(
                'Invalid {} date range. Start date may not equal end '
                'date. Got {} = {} for \'{}\''.format(
                    self.__class__.__name__,
                    self.start.strftime('%Y-%m-%d %Z'),
                    self.end.strftime('%Y-%m-%d %Z'),
                    self.name))

    @property
    def rstart(self):
        return arrow.Arrow.fromdatetime(self.start, self.start.tzinfo).to('utc')

    @property
    def rend(self):
        return arrow.Arrow.fromdatetime(self.end, self.end.tzinfo).to('utc')
