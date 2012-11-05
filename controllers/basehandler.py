import webapp2

__all__ = ["BaseHandler"]

class BaseHandler(webapp2.RequestHandler):

    def render(self, content):
        if content == "null":
            self.abort(404)

        if self.request.get("callback"):
            content = "%s(%s)" % (self.request.get("callback"), content)

        #
        self.response.headers["Content-Type"] = "application/json; charset=utf-8"

        # http://en.wikipedia.org/wiki/List_of_HTTP_header_fields
        self.response.headers["Cache-Control"] = "max-age=0, private, must-revalidate"
        self.response.headers["X-Content-Type-Options"] = "nosniff"

        self.response.write(content)
