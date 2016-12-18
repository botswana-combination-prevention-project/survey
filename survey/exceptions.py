# coding=utf-8


class SurveyScheduleError(Exception):
    pass


class AddSurveyDateError(Exception):
    pass


class AddSurveyMapAreaError(Exception):
    pass


class AddSurveyNameError(Exception):
    pass


class AddSurveyOverlapError(Exception):
    pass


class SurveyError(Exception):
    pass


class RegistryNotLoaded(Exception):
    pass


class AlreadyRegistered(Exception):
    pass
