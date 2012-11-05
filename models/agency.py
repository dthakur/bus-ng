from google.appengine.ext import ndb

from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from utils import url

import logging

__all__ = ["Agency"]

class Agency(ndb.Model):

    _use_cache  = True
    _use_memcache = True
    _use_datastore = True
    _memcache_timeout = 604800

    tag = ndb.StringProperty()
    title = ndb.StringProperty(indexed=False)
    region_title = ndb.StringProperty(indexed=False)

    @classmethod
    def properties(cls, agency_tag):
        logging.info("properties@Agency...")
        return ndb.Key("Agency", agency_tag).get()

    @classmethod
    def get_or_fetch(cls):
        logging.info("get_or_fetch@Agency...")

        results = ndb.get_multi(cls.query().fetch(keys_only=True))
        if len(results) == 0:
            results = cls.from_nextbus()

        agencies = {}
        for agency in results:
            agencies[agency.tag] = agency

        return agencies

    @classmethod
    def from_nextbus(cls):
        logging.info("from_nextbus@Agency...")

        agencies = []
        etree = url.fetch_nextbus_url({ "command" : "agencyList" })
        for elem in etree.findall("agency"):
            tag = elem.get("tag")
            title = elem.get("title")
            region_title = elem.get("regionTitle")
            r = Agency(id = tag, tag = tag, title = title, region_title = region_title)
            agencies.append(r)

        try:
            ndb.put_multi(agencies, max_entity_groups_per_rpc = 16)
        except CapabilityDisabledError:
            # fail gracefully here
            pass

#        cls.create_document(agencies)

        return agencies

#    @classmethod
#    def create_document(cls, agencies):
#        from google.appengine.api import search
#        _INDEX_NAME="agencies"
#        for agency in agencies:
#            doc_id = search.Document(fields=[search.TextField(name='tag', value=agency.tag), search.TextField(name='title', value=agency.title)])
#            search.Index(name=_INDEX_NAME).put(doc_id)
