import urllib
import urllib2
import logging
import xml.etree.cElementTree as etree

URL = "http://webservices.nextbus.com/service/publicXMLFeed"

def fetch_nextbus_url(parameters):
    url = "?".join([URL, urllib.urlencode(parameters, True)])
    req = urllib2.Request(url)
    try:
        result = urllib2.urlopen(req)
    except urllib2.URLError, e:
        logging.error("Exception in urllib: %s" % e)
        return []

    return etree.parse(result)
