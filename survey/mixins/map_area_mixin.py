from django.conf import settings

from ..exceptions import SurveyMapAreaError


class MapAreaMixin:

    def __init__(self, map_area=None, map_areas=None, **kwargs):
        super().__init__(**kwargs)
        self.map_area = map_area or self.get_map_area()
        self.map_areas = map_areas or []
        if not self.map_areas and self.map_area:
            self.map_areas = [self.map_area]

    @property
    def map_area_display(self):
        return ' '.join([word[0].upper() for word in self.map_area.split('_')])

    def get_map_area(self):
        return self._map_area_from_settings()

    def _map_area_from_settings(self):
        try:
            return settings.CURRENT_MAP_AREA
        except AttributeError:
            pass
        return None

    def validate_map_area(self):

        if self.map_area and self.map_areas:

            if self.map_area not in self.map_areas:
                raise SurveyMapAreaError(
                    'Invalid {} map area. {} is not a valid map '
                    'area.'.format(self.__class__.__name__, self.map_area))

            if self.map_area not in self.map_areas:
                raise SurveyMapAreaError(
                    'Invalid {} map area. {} is not a '
                    'valid map area.'.format(self.__class__.__name__, self.map_area))

            if (self._map_area_from_settings() and
                    self._map_area_from_settings() != self.map_area):
                raise SurveyMapAreaError(
                    'Invalid {} map area. Map area is specified twice. '
                    'Got \'{}\' from settings and \'{}\' from class.'.format(
                        self.__class__.__name__,
                        self._map_area_from_settings(),
                        self.map_area))
