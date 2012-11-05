from basehandler import BaseHandler

from models import Direction

from utils import ratelimit, cache, formatter

__all__ = ["Directions"]

class Directions(BaseHandler):
    @ratelimit.ratelimit(minutes = 3, requests = 10)
    def get(self, agency_tag, route_tag, direction_tag = None):

        content = self.direction(agency_tag, route_tag, direction_tag) if direction_tag else self.directions(agency_tag, route_tag)

        self.render(content)

    @cache.cache(time = 604800)
    def directions(self, agency_tag, route_tag):
        return formatter.JSON(Direction.get_or_fetch(agency_tag, route_tag))

    @cache.cache(time = 604800)
    def direction(self, agency_tag, route_tag, direction_tag):
        return formatter.JSON(Direction.properties(agency_tag, route_tag, direction_tag))
