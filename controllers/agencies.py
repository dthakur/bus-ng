from basehandler import BaseHandler

from models import Agency

from utils import ratelimit, cache, formatter

__all__ = ["Agencies"]

class Agencies(BaseHandler):
    @ratelimit.ratelimit(minutes = 3, requests = 10)
    def get(self, agency_tag = None):
        content = self.agency(agency_tag) if agency_tag else self.agencies()

        self.render(content)

    @cache.cache(time = 604800)
    def agencies(self):
        return formatter.JSON(Agency.get_or_fetch())

    @cache.cache(time = 604800)
    def agency(self, agency_tag):
        return formatter.JSON(Agency.properties(agency_tag))
