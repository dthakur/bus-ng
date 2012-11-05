from google.appengine.api import xmpp

from basehandler import BaseHandler

from models import Route, Estimation

from utils import formatter

__all__ = ["XMPP", "XMMPPresence"]

class XMPP(BaseHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)

        if message.body == "routes":
            r = Route.get_or_fetch("mbta")
            message.reply(", ".join(r.keys()))
        elif message.body == "@home":
            e = Estimation.get_or_fetch("mbta", "747", "747_0_var0", "1807")
            message.reply(formatter.JSON(e))
        elif message.body == "@office":
            e = Estimation.get_or_fetch("mbta", "747", "747_0_var1", "2231_1")
            message.reply(formatter.JSON(e))
        else:
            message.reply("...")

class XMMPPresence(BaseHandler):
    def post(self, available):
        import logging

        user = self.request.get("from").split("/")[0]
        if available == "unavailable":
            logging.info("%s has gone offline..." % user)
        else:
            logging.info("%s comes back online..." % user)
