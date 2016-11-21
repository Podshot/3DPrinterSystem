import tornado.web
import tornado.ioloop
import tornado.httpserver

import os

from web.frontend.profile import MainProfileHandler, SubmissionsHandler, LoginHijack, NewSubmissionHandler, SubmitHandler
from frontend import ui_modules
from web.frontend.profile import RemoveSubmissionHandler
from backend import GetAllSubmissionsHandler, GetSubmissionHandler, ModifySubmissionHandler, AuthenticationHandler

settings = {
    "cookie_secret": "test_cookie",
    "login_url": "/login",
    "template_path": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates"),
    "ui_modules": ui_modules,
    #"debug": True,
}

class MainHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.redirect("/login")

if __name__ == "__main__":
    app = tornado.web.Application([
                                   (r"/", MainHandler),
                                   (r"/submit", SubmitHandler),
                                   (r"/new_submission", NewSubmissionHandler),
                                   (r"/login", LoginHijack),
                                   (r"/profile", MainProfileHandler),
                                   (r"/profile/submissions", SubmissionsHandler),
                                   (r"/profile/submissions/remove/([^/]+)", RemoveSubmissionHandler),
                                   (r"/api/authenticate", AuthenticationHandler),
                                   (r"/api/submission/get_all", GetAllSubmissionsHandler),
                                   (r"/api/submission", GetSubmissionHandler),
                                   (r"/api/submission/update", ModifySubmissionHandler),
                                   ],
                                  **settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(80)
    #app.listen(80)
    tornado.ioloop.IOLoop.current().start()
