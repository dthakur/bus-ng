from google.appengine.api import memcache

import logging

class cache(object):
    def __init__(self, time=3600, key=None):
        self.time = time
        self.key  = key

    def __call__(self, f):
        def func(*args, **kwargs):
            key = self.key
            if self.key is None:
                key = "%s@%s" % (args[0].__class__.__name__, "@".join(args[1:]))

            data = memcache.get(key)
            if data is not None:
                logging.info("cache HIT: key:%s", key)
                return data

            logging.info("cache MISS: key:%s", key)
            data = f(*args, **kwargs)
            memcache.set(key, data, self.time)
            return data

        func.func_name = f.func_name
        return func
