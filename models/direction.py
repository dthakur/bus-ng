from google.appengine.ext import ndb

from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from utils import url
import logging

__all__ = ["Direction"]

class Direction(ndb.Model):

    _use_cache  = True
    _use_datastore = True
    _use_memcache = True
    _memcache_timeout = 604800

    tag = ndb.StringProperty()
    title  = ndb.StringProperty(indexed = False)
    name  = ndb.StringProperty(indexed = False)
    use_for_UI = ndb.BooleanProperty(indexed = False)

    @classmethod
    def properties(cls, agency_tag, route_tag, direction_tag):
        logging.info("properties@Direction...")
        return ndb.Key("Direction", direction_tag, parent = ndb.Key("Route", route_tag, parent = ndb.Key("Agency", agency_tag))).get()

    @classmethod
    def get_or_fetch(cls, agency_tag, route_tag):
        logging.info("get_or_fetch@Direction..")

        # Ancestor
        results = ndb.get_multi(cls.query(ancestor = ndb.Key("Route", route_tag, parent = ndb.Key("Agency", agency_tag))).fetch(keys_only=True))
        if len(results) == 0:
            results = cls.from_nextbus(agency_tag, route_tag)

        directions = {}
        for direction in results:
            directions[direction.tag] = direction

        return directions

    @classmethod
    def from_nextbus(cls, agency_tag, route_tag):
        logging.info("from_nextbus@Direction..")

        etree = url.fetch_nextbus_url({ "a" : agency_tag, "command" : "routeConfig", "r" : route_tag.replace("__", " "), "terse" : "True"})

        directions = []
        for elem in etree.findall("route/direction"):
            tag = elem.get("tag")
            # there are some directions named like 107_0_107B*uncon
            if tag.find("*") != -1:
                tag = tag.replace("*", "_")
            if tag.find("/") != -1:
                tag = tag.replace("/", "_")
            title = elem.get("title")
            name = elem.get("name")
            use_for_UI = bool(elem.get("useForUI"))
            d = Direction(id = tag, parent = ndb.Key("Route", route_tag, parent = ndb.Key("Agency", agency_tag)), tag = tag, title = title, name = name, use_for_UI = use_for_UI)
            directions.append(d)

        try:
            ndb.put_multi(directions)
        except CapabilityDisabledError:
            # fail gracefully here
            pass

        return directions
