from google.appengine.ext import ndb

from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from utils import url
import logging

__all__ = ["Stop"]

from direction import Direction

class Stop(ndb.Model):

    _use_cache  = True
    _use_memcache = True
    _use_datastore = True
    _memcache_timeout = 604800

    tag = ndb.StringProperty()
    title = ndb.StringProperty(indexed=False)
    location = ndb.GeoPtProperty(indexed=False)
    stop_id = ndb.StringProperty(indexed=False)
    directions = ndb.KeyProperty(kind = "Direction", repeated = True)

    @classmethod
    def properties(cls, agency_tag, route_tag, direction_tag, stop_tag):
        logging.info("properties@Stop...")
        stop_key = "%s@%s" % (agency_tag, stop_tag)
        direction_key = ndb.Key("Direction", direction_tag, parent = ndb.Key("Route", route_tag, parent = ndb.Key("Agency", agency_tag)))
        stop = ndb.Key("Stop", stop_key).get()
        return stop if direction_key in stop.directions else {}

    @classmethod
    def get_or_fetch(cls, agency_tag, route_tag, direction_tag):
        logging.info("get_or_fetch@Direction..")

        direction_key = ndb.Key("Direction", direction_tag, parent = ndb.Key("Route", route_tag, parent = ndb.Key("Agency", agency_tag)))
        # Ancestor
        results = ndb.get_multi(cls.query(Stop.directions.IN([direction_key])).fetch(keys_only=True))
        if len(results) == 0:
            results = cls.from_nextbus(agency_tag, route_tag, direction_tag)

        stops = {}
        for stop in results:
            stops[stop.tag] = stop

        #cls.query_document()
        return stops

    @classmethod
    def from_nextbus(cls, agency_tag, route_tag, direction_tag):
        logging.info("from_nextbus@Stop...")

        etree = url.fetch_nextbus_url({ "a" : agency_tag, "command" : "routeConfig", "r" : route_tag.replace("__", " "), "terse" : "True"})

        # create a lookup table which maps stop to directions that it belong
        #
        # stops2directions[stop_tag] -> direction_tag(s)
        stops2directions = {}
        for elem in etree.findall("route/direction"):
            direction_tag_ = elem.get("tag")
            # there are some directions named like 107_0_107B*uncon
            if direction_tag_.find("*") != -1:
                direction_tag_ = direction_tag_.replace("*", "_")
            if direction_tag_.find("/") != -1:
                direction_tag_ = direction_tag_.replace("/", "_")
            for stop_elem_ in elem.findall("stop"):
                stops2directions.setdefault(stop_elem_.get("tag"), set()).add(direction_tag_)

        # prefetch stops to solve staircase pattern caused by get calls in the loop below
        #
        # https://groups.google.com/forum/#!topic/appengine-ndb-discuss/wgNtAMwirJo
        for elem in etree.findall("route/stop"):
            tag = elem.get("tag")

            # some directions report unused stops so ignore them...
            if stops2directions.has_key(tag):
                ndb.Key("Stop", "%s@%s" % (agency_tag, tag)).get_async()

        # create/update stop entities
        #
        stops = []
        for elem in etree.findall("route/stop"):
            tag = elem.get("tag")

            # some directions report unused stops so ignore them...
            if stops2directions.has_key(tag):
                title = elem.get("title")
                stop_id = elem.get("stopId")
                location = ndb.GeoPt(float(elem.get("lat")), float(elem.get("lon")))
                directions = [ndb.Key("Direction", direction_tag_, parent = ndb.Key("Route", route_tag, parent = ndb.Key("Agency", agency_tag))) for direction_tag_ in stops2directions[tag]]
                stop_key = "%s@%s" % (agency_tag, tag)
                ####
                obj = ndb.Key("Stop", stop_key).get()
                if obj:
                    directions += obj.directions
                ####
                s = Stop(id = stop_key, tag = tag, title = title, stop_id = stop_id, location = location, directions = directions)
                stops.append(s)

        try:
            ndb.put_multi(stops)
        except CapabilityDisabledError:
            # fail gracefully here
            pass

        #cls.create_document(stops)

        # filter out other directions
        direction_key = ndb.Key("Direction", direction_tag, parent = ndb.Key("Route", route_tag, parent = ndb.Key("Agency", agency_tag)))
        return [stop for stop in stops if direction_key in stop.directions]

#    @classmethod
#    def query_document(cls):
#        logging.info("query_document query_document query_document")
#        from google.appengine.api import search
#        _INDEX_NAME="stops"
#        index = search.Index(_INDEX_NAME)
#        query = "distance(location, geopoint(42.3428121, -71.101163)) < 200"
#        search_results = index.search(query)
#        for doc in search_results:
#            logging.info(doc)

#    @classmethod
#    def create_document(cls, stops):
#        from google.appengine.api import search
#        _INDEX_NAME="stops"
#        for stop in stops:
#            doc_id = search.Document(fields=[search.TextField(name="tag", value=stop.tag),
#                                            search.TextField(name="title", value=stop.title),
#                                            search.GeoField(name="location", value=search.GeoPoint(stop.location.lat, stop.location.lon))])
#
#            search.Index(name=_INDEX_NAME).put(doc_id)
