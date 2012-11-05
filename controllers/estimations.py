from google.appengine.api import memcache

from basehandler import BaseHandler

from models import Estimation

from utils import ratelimit, cache, formatter

import datetime

__all__ = ["Estimations"]

class Estimations(BaseHandler):

    HTTP_DATE_FMT = "%a, %d %b %Y %H:%M:%S GMT"

    def last_modified(self, agency_tag, route_tag, direction_tag, stop_tag):
        key = "LastModified_%s@%s@%s@%s" %(agency_tag, route_tag, direction_tag, stop_tag)

        last_modified = memcache.get(key)
        if last_modified is None:
            last_modified = datetime.datetime.now()
            memcache.set(key, last_modified, 30)

        return last_modified

    def head(self, agency_tag, route_tag, direction_tag, stop_tag):
        last_modified = self.last_modified(agency_tag, route_tag, direction_tag, stop_tag)

        if "If-Modified-Since" in self.request.headers:
            last_seen = datetime.datetime.strptime(self.request.headers["If-Modified-Since"], self.HTTP_DATE_FMT)
            if last_seen.replace(microsecond=0) >= last_modified.replace(microsecond=0):
                self.response.headers["X-Poll-Interval"] = "30"
                self.abort(304)

        self.get(agency_tag, route_tag, direction_tag, stop_tag)

    @ratelimit.ratelimit(minutes = 3, requests = 10)
    def get(self, agency_tag, route_tag, direction_tag, stop_tag):

        content = self.estimations(agency_tag, route_tag, direction_tag, stop_tag)

        # add extra headers
        self.response.headers["X-Poll-Interval"] = "30"
        self.response.headers["Last-Modified"] = self.last_modified(agency_tag, route_tag, direction_tag, stop_tag).strftime(self.HTTP_DATE_FMT)

        self.render(content)

    @cache.cache(time = 30)
    def estimations(self, agency_tag, route_tag, direction_tag, stop_tag):
        return formatter.JSON(Estimation.get_or_fetch(agency_tag, route_tag, direction_tag, stop_tag))
