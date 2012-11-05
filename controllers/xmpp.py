from google.appengine.api import xmpp

from basehandler import BaseHandler

from models import Route, Estimation

from utils import formatter

__all__ = ["XMPP"]

class XMPP(BaseHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        user = message.sender.split("/")[0]

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
