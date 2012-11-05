from google.appengine.ext import ndb
from google.appengine.ext.ndb import model, query
from google.appengine.api import memcache
from google.appengine.api import users

import json
import datetime
import time

from tz import UTC, EST

# https://gist.github.com/1572547
def JSON(obj, prefetch = False, attr = None):
    def to_json(obj):
        if hasattr(obj, "to_dict"):
            return getattr(obj, "to_dict")()

        if isinstance(obj, query.Query):
            return list(obj)

        elif isinstance(obj, datetime.datetime):
            return obj.replace(tzinfo=UTC()).astimezone(EST()).strftime("%a, %d %b %Y %H:%M:%S")

        elif isinstance(obj, time.struct_time):
            return list(obj)

        elif isinstance(obj, users.User):
            output = {}
            methods = ["nickname", "email", "auth_domain"]
            for method in methods:
                output[method] = getattr(obj, method)()
            return output

        elif isinstance(obj, model.Key):
            return obj.get()

        elif isinstance(obj, ndb.Future):
            return obj.get_result()

        else:
            return obj.__dict__

    if prefetch and attr is not None:
        for i in obj.iteritems():
            for o in getattr(i[1], attr):
                o.get_async()
    return json.dumps(obj, default = to_json, indent = 2, sort_keys = True)
