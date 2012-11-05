from google.appengine.ext import ndb

from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from utils import url
import logging

__all__ = ["Route"]

class Route(ndb.Model):

    _use_cache  = True
    _use_memcache = True
    _use_datastore = True
    _memcache_timeout = 604800

    tag = ndb.StringProperty()
    title  = ndb.StringProperty(indexed=False)

    @classmethod
    def properties(cls, agency_tag, route_tag):
        logging.info("properties@Agency...")
        return ndb.Key("Route", route_tag, parent =  ndb.Key("Agency", agency_tag)).get()

    @classmethod
    def get_or_fetch(cls, agency_tag):
        logging.info("get_or_fetch@Route...")

        results = ndb.get_multi(cls.query(ancestor = ndb.Key("Agency", agency_tag)).fetch(keys_only=True))
        if len(results) == 0:
            results = cls.from_nextbus(agency_tag)

        routes = {}
        for route in results:
            routes[route.tag] = route

        return routes

    @classmethod
    def from_nextbus(cls, agency_tag):
        logging.info("from_nextbus@Route...")

        routes = []
        etree = url.fetch_nextbus_url({ "a" : agency_tag, "command" : "routeList" })
        for elem in etree.findall("route"):
            tag = elem.get("tag")
            if tag.find(" ") != -1:
                tag = tag.replace(" ", "__")
            title = elem.get("title")
            r = Route(id = tag, parent = ndb.Key("Agency", agency_tag), tag = tag, title = title)
            routes.append(r)

        try:
            ndb.put_multi(routes, max_entity_groups_per_rpc = 16)
        except CapabilityDisabledError:
            # fail gracefully here
            pass

        return routes
