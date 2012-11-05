from basehandler import BaseHandler

from models import Route, Agency

from utils import ratelimit, cache, formatter

__all__ = ["Routes"]

class Routes(BaseHandler):
    @ratelimit.ratelimit(minutes = 3, requests = 10)
    def get(self, agency_tag = None, route_tag = None):

        if agency_tag and route_tag:
            content = self.route(agency_tag, route_tag)
        elif agency_tag:
            content = self.routes(agency_tag)
        else:
            content = self.agencies_and_routes()

        self.render(content)

    @cache.cache(time = 604800)
    def routes(self, agency_tag):
        return formatter.JSON(Route.get_or_fetch(agency_tag))

    @cache.cache(time = 604800)
    def route(self, agency_tag, route_tag):
        return formatter.JSON(Route.properties(agency_tag, route_tag))

    @cache.cache(time = 86400)
    def agencies_and_routes(self):
        all_routes = {}
        for agency in Agency.get_or_fetch().iteritems():
            agency_tag = agency[0]
            agency_model_dict = agency[1].to_dict()
            agency_model_dict.setdefault("routes", []).append(Route.get_or_fetch(agency_tag))
            all_routes[agency_tag] = agency_model_dict

        return formatter.JSON(all_routes)
