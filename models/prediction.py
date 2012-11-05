from google.appengine.ext import ndb

from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError


import logging
import datetime

__all__ = ["Prediction"]

class Prediction(ndb.Model):

    _use_cache  = False
    _use_memcache = True
    _use_datastore = False
    _memcache_timeout = 30

    affected_by_layover = ndb.BooleanProperty(indexed = False)
    block = ndb.StringProperty(indexed = False)
    delayed = ndb.BooleanProperty(indexed = False)
    dir_tag = ndb.StringProperty(indexed = False)
    epoch_time = ndb.IntegerProperty(indexed = False)
    is_departure = ndb.BooleanProperty(indexed = False)
    minutes = ndb.IntegerProperty(indexed = False)
    seconds = ndb.IntegerProperty(indexed = False)
    trip_tag = ndb.StringProperty(indexed = False)
    vehicle = ndb.IntegerProperty(indexed = False)

    _agency_tag = None
    _route_tag = None
    _direction_tag = None
    _stop_tag = None

    @ndb.ComputedProperty
    def human_readable_time(self):
        if self.epoch_time:
            return datetime.datetime.fromtimestamp(self.epoch_time/1000)

    @ndb.ComputedProperty
    def human_readable_dir_title(self):
        if self._direction_tag:
            return ndb.Key("Direction", self._direction_tag, parent = ndb.Key("Route", self._route_tag, parent = ndb.Key("Agency", self._agency_tag))).get().title

    @classmethod
    def from_nextbus(cls, etree, agency_tag, route_tag, direction_tag, stop_tag):
        logging.info("from_nextbus@Prediction...")

        cls._agency_tag = agency_tag
        cls._route_tag = route_tag
        cls._direction_tag = direction_tag
        cls._stop_tag = stop_tag

        predictions = []
        for prediction in etree.findall("predictions/direction/prediction"):
            epoch_time = int(prediction.get("epochTime"))
            minutes = int(prediction.get("minutes"))
            seconds = int(prediction.get("seconds"))
            is_departure = True if prediction.get("isDeparture") == "true" else False
            affected_by_layover = True if prediction.get("affected_by_layover") else False
            block = prediction.get("block")
            trip_tag = prediction.get("tripTag")
            vehicle = int(prediction.get("vehicle"))
            dir_tag = prediction.get("dirTag")
            delayed = True if prediction.get("delayed") else False
            p = Prediction(id = trip_tag, minutes = minutes, seconds = seconds, is_departure = is_departure, block = block, dir_tag = dir_tag, trip_tag = trip_tag, vehicle = vehicle, delayed = delayed, affected_by_layover = affected_by_layover, epoch_time = epoch_time)
            predictions.append(p)

        try:
            ndb.put_multi(predictions)
        except CapabilityDisabledError:
           # fail gracefully here
            pass

        return predictions
