from basehandler import BaseHandler

from models import Stop

from utils import ratelimit, cache, formatter

__all__ = ["Stops"]

class Stops(BaseHandler):
    @ratelimit.ratelimit(minutes = 3, requests = 10)
    def get(self, agency_tag, route_tag, direction_tag, stop_tag = None):

        content = self.stop(agency_tag, route_tag, direction_tag, stop_tag) if stop_tag else self.stops(agency_tag, route_tag, direction_tag)

        self.render(content)

    @cache.cache(time = 86400)
    def stops(self, agency_tag, route_tag, direction_tag):
        return formatter.JSON(Stop.get_or_fetch(agency_tag, route_tag, direction_tag), prefetch = True, attr = "directions")

    @cache.cache(time = 86400)
    def stop(self, agency_tag, route_tag, direction_tag, stop_tag):
        return formatter.JSON(Stop.properties(agency_tag, route_tag, direction_tag, stop_tag))
