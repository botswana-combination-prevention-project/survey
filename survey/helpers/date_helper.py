import arrow


class DateError(Exception):
    pass


class DateHelper:

    def __init__(self, start=None, end=None):
        self.start = arrow.Arrow.fromdatetime(
            start, start.tzinfo).to('utc').floor('hour').datetime
        self.end = arrow.Arrow.fromdatetime(
            end, end.tzinfo).to('utc').ceil('hour').datetime

        if self.start > self.end:
            start = self.start.strftime('%Y-%m-%d %Z')
            end = self.end.strftime('%Y-%m-%d %Z')
            raise DateError(
                'Invalid date range. Start date may not precede end '
                'date. Got {start} > {end}')

        if self.start == self.end:
            start = self.start.strftime('%Y-%m-%d %Z')
            end = self.end.strftime('%Y-%m-%d %Z')
            raise DateError(
                'Invalid date range. Start date may not equal end '
                'date. Got {start} = {end}')

    @property
    def rstart(self):
        return arrow.Arrow.fromdatetime(self.start, self.start.tzinfo).to('utc')

    @property
    def rend(self):
        return arrow.Arrow.fromdatetime(self.end, self.end.tzinfo).to('utc')
