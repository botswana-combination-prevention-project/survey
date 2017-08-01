
class MapAreaHelper:

    def __init__(self, map_area=None, map_areas=None):
        self.map_area = map_area or self.get_map_area()
        self.map_areas = map_areas or []
        if not self.map_areas and self.map_area:
            self.map_areas = [self.map_area]

    @property
    def map_area_display(self):
        return ' '.join(self.map_area.split('_')).title()

    def get_map_area(self):
        """Returns a map area from AppConfig."""
        from edc_map.site_mappers import site_mappers
        return site_mappers.current_map_area

#     def validate_map_area(self):
#
#         if self.map_area and self.map_areas:
#
#             if self.map_area not in self.map_areas:
#                 raise SurveyMapAreaError(
#                     'Invalid {} map area. {} is not a valid map '
#                     'area.'.format(self.__class__.__name__, self.map_area))
#
#             if self.map_area not in self.map_areas:
#                 raise SurveyMapAreaError(
#                     'Invalid {} map area. {} is not a '
#                     'valid map area.'.format(self.__class__.__name__, self.map_area))
#
#             if self.get_map_area() != self.map_area:
#                 raise SurveyMapAreaError(
#                     'Invalid {} map area. Map area is specified twice. '
#                     'Got \'{}\' from settings and \'{}\' from class.'.format(
#                         self.__class__.__name__,
#                         self.get_map_area(),
#                         self.map_area))
