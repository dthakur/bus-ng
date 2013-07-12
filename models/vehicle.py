from google.appengine.ext import ndb

from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from utils import url
import logging

__all__ = ["Vehicle"]

class Vehicle(ndb.Model):

    _use_cache  = False
    _use_memcache = True
    _use_datastore = False
    _memcache_timeout = 30

    vehicle_id = ndb.StringProperty()
    route_tag  = ndb.StringProperty(indexed=False)
    dir_tag  = ndb.StringProperty(indexed=False)
    location = ndb.GeoPtProperty(indexed=False)
    secs_since_report = ndb.IntegerProperty(indexed=False)
    predictable = ndb.BooleanProperty(indexed=False)
    heading = ndb.IntegerProperty(indexed=False)
    speedKmHr = ndb.FloatProperty(indexed=False)

#    @ndb.ComputedProperty
#    def human_readable_dir_title(self):
#        if self.dir_tag:
#            obj = ndb.Key("Direction", self.dir_tag, parent = ndb.Key("Route", self.route_tag)).get()
#            if obj:
#                return obj.title

    @classmethod
    def get_or_fetch(cls, agency_tag, route_tag = None):
        logging.info("get_or_fetch@Route...")

        results = cls.from_nextbus(agency_tag, route_tag)

        vehicles = {}
        for vehicle in results:
            vehicles[vehicle.vehicle_id] = vehicle

        return vehicles

    @classmethod
    def from_nextbus(cls, agency_tag, route_tag):
        logging.info("from_nextbus@Vehicle...")

        if route_tag:
            etree = url.fetch_nextbus_url({ "a" : agency_tag, "command" : "vehicleLocations", "r" : route_tag })
        else:
            etree = url.fetch_nextbus_url({ "a" : agency_tag, "command" : "vehicleLocations" })

        vehicles = []
        for elem in etree.findall("vehicle"):
            vehicle_id = elem.get("id")
            route_tag = elem.get("routeTag")
            dir_tag = elem.get("dirTag")
            location = ndb.GeoPt(float(elem.get("lat")), float(elem.get("lon")))
            secs_since_report = int(elem.get("secsSinceReport"))
            predictable = bool(elem.get("predictable"))
            heading = int(elem.get("heading"))
            try:
                speedKmHr = float(elem.get("speedKmHr"))
            except:
                speedKmHr = 0
            v = Vehicle(id = vehicle_id, vehicle_id = vehicle_id, route_tag = route_tag, dir_tag = dir_tag, location = location, secs_since_report = secs_since_report, predictable = predictable, heading= heading, speedKmHr = speedKmHr)
            vehicles.append(v)

        try:
            ndb.put_multi(vehicles, max_entity_groups_per_rpc = 16)
        except CapabilityDisabledError:
            # fail gracefully here
            pass

        return vehicles
