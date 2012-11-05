from google.appengine.ext import ndb

from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

import logging
from utils import url
import datetime

from prediction import Prediction

__all__ = ["Estimation"]

class Estimation(ndb.Model):

    _use_cache  = False
    _use_memcache = True
    _use_datastore = False
    _memcache_timeout = 30

    agency_title = ndb.StringProperty(indexed = False)
    route_title = ndb.StringProperty(indexed = False)
    route_tag = ndb.StringProperty(indexed = False)
    stop_title = ndb.StringProperty(indexed = False)
    stop_tag = ndb.StringProperty(indexed = False)
    predictions = ndb.KeyProperty(kind = "Prediction", repeated = True)
    created = ndb.DateTimeProperty(auto_now_add = True)

    @ndb.ComputedProperty
    def expires(self):
        return self.created + datetime.timedelta(seconds = 30)

    @classmethod
    def get_or_fetch(cls, agency_tag, route_tag, direction_tag, stop_tag):
        logging.info("get_or_fetch@Estimation...")

        results = cls.from_nextbus(agency_tag, route_tag, direction_tag, stop_tag)

        estimations = {}
        for estimation in results:
            estimations["estimations"] = estimation

        return estimations

    @classmethod
    def from_nextbus(cls, agency_tag, route_tag, direction_tag, stop_tag):
        logging.info("from_nextbus@Estimation...")

        etree = url.fetch_nextbus_url({ "a" : agency_tag, "command" : "predictions", "s" : stop_tag, "r" : route_tag.replace("__", " ")})

        prediction_keys = [prediction.key for prediction in Prediction.from_nextbus(etree, agency_tag, route_tag, direction_tag, stop_tag)]

        estimations = []
        for elem in etree.findall("predictions"):
            route_tag = elem.get("routeTag")
            stop_tag = elem.get("stopTag")
            agency_title = elem.get("agencyTitle")
            route_title = elem.get("routeTitle")
            stop_title =  elem.get("stopTitle")
            key = "%s@%s@%s@%s" % (agency_tag, route_tag, direction_tag, stop_tag)
            e = Estimation(id = key, route_tag = route_tag, stop_tag = stop_tag, agency_title = agency_title, route_title = route_title, stop_title = stop_title, predictions = prediction_keys)
            estimations.append(e)

        try:
            ndb.put_multi(estimations)
        except CapabilityDisabledError:
            # fail gracefully here
            pass

        return estimations
