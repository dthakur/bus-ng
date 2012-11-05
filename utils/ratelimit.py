from google.appengine.api import memcache

import functools
import datetime
import time

# http://code.google.com/p/gaedjango-ratelimitcache/
class ratelimit(object):
    """
    A memcached backed rate limiting decorator for Google App Engine.
    """
    # The time period
    minutes = 3
    # Number of allowed requests in that time period
    requests = 10
    # Prefix for memcache key
    prefix = "rl-"
    # Expiration time
    expire_after = (minutes + 1) * 60

    def __init__(self, **options):
        for key, value in options.items():
            setattr(self, key, value)

    def __call__(self, fn):
        def wrapper(handler, *args, **kwargs):
            return self.view_wrapper(handler, fn, *args, **kwargs)
        functools.update_wrapper(wrapper, fn)
        return wrapper

    def view_wrapper(self, handler, fn, *args, **kwargs):
        # Pass if not ratelimited
        if not self.should_ratelimit(handler):
            return fn(handler, *args, **kwargs)

        # Rate limit if exceeded
        sum_of_requests = self._get_sum_of_requests(handler)

        handler.response.headers["X-RateLimit-Limit"] = str(self.requests)
        handler.response.headers["X-RateLimit-Remaining"] = str(self.requests - sum_of_requests)
        if sum_of_requests >= self.requests:
            return self.disallowed(handler)

        # Count successful request
        self._count_request(handler)
        # Pass
        return fn(handler, *args, **kwargs)

    def should_ratelimit(self, handler):
        """
        Returns a boolean. Over-ride this method if you need only certain types
        of requests to rate limit.
        The default behavior is to rate limit every request.
        """
        return False if handler.request.remote_addr in ["127.0.0.1"] else True

    def disallowed(self, handler):
        """
        Returns a 403 error
        """
        raise handler.abort(403)

    def key_extra(self, handler):
        """
        Returns the key extra that filters the request. Over-ride this method
        if you want to use a different extra than the remote IP address.
        """
        return handler.request.remote_addr

    def _increase_cache(self, key):
        """
        Increases a cache value, creates the key on demand.
        """
        added = memcache.add(key, 1, time=self.expire_after)
        if not added:
            memcache.incr(key)

    def _get_current_key(self, handler):
        """
        Returns the current key name.
        """
        return "%s%s-%s" % (self.prefix, self.key_extra(handler),
            datetime.datetime.utcnow().strftime("%Y%m%d%H%M"))

    def _count_request(self, handler):
        """
        Counts the request in the cache.
        """
        self._increase_cache(self._get_current_key(handler))

    def _keys_to_check(self, handler):
        """
        Returns a list of keys to check.
        """
        extra = self.key_extra(handler)
        now = datetime.datetime.utcnow()
        return [
            "%s%s-%s" % (
                self.prefix,
                extra,
                (now - datetime.timedelta(minutes = minute)).strftime("%Y%m%d%H%M")
            ) for minute in range(self.minutes + 1)
        ]

    def _get_counters(self, handler):
        """
        Returns a list of counters to check.
        """
        return memcache.get_multi(self._keys_to_check(handler))

    def _get_sum_of_requests(self, handler):
        """
        Returns the sum of the former requests.
        """
        return sum(self._get_counters(handler).values())
