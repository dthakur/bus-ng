from google.appengine.api import xmpp
from google.appengine.ext import ereporter

import os
import webapp2
import jinja2

import logging

import controllers

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def handle_403(request, response, exception):
    logging.warn("Rate limiting %s for %s" % (request.remote_addr, request.url))
    response.write("You have been rate-limited")
    response.set_status(403)

def handle_error(request, response, exception):
    status_int = hasattr(exception, "status_int") and exception.status_int or 500
    c = {"exception": str(exception), "status" : status_int}

    template = jinja_environment.get_template("templates/error.html")
    response.write(template.render(c))
    response.set_status(status_int)

app = webapp2.WSGIApplication([
    ("/agencies/", controllers.Agencies),
    ("/agencies/([\w-]+)", controllers.Agencies),
    ("/agencies/([\w-]+)/vehicles/", controllers.Vehicles),
    ("/agencies/all/routes/", controllers.Routes),
    ("/agencies/([\w-]+)/routes/", controllers.Routes),
    ("/agencies/([\w-]+)/routes/(\w+)", controllers.Routes),
    ("/agencies/([\w-]+)/routes/(\w+)/vehicles/", controllers.Vehicles),
    ("/agencies/([\w-]+)/routes/(\w+)/directions/", controllers.Directions),
    ("/agencies/([\w-]+)/routes/(\w+)/directions/(\w+)", controllers.Directions),
    ("/agencies/([\w-]+)/routes/(\w+)/directions/(\w+)/stops/", controllers.Stops),
    ("/agencies/([\w-]+)/routes/(\w+)/directions/(\w+)/stops/(\w+)", controllers.Stops),
    ("/agencies/([\w-]+)/routes/(\w+)/directions/(\w+)/stops/(\w+)/predictions/", controllers.Estimations),
    ("/_ah/xmpp/message/chat/", controllers.XMPP),
    ])

app.error_handlers[304] = handle_error
app.error_handlers[403] = handle_403
app.error_handlers[404] = handle_error
app.error_handlers[500] = handle_error

ereporter.register_logger()

def main():
    app.run()

if __name__ == "__main__":
    main()
