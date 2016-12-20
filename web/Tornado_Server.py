import tornado.web
import tornado.ioloop
import tornado.httpserver

import os

from frontend.profile import MainProfileHandler, SubmissionsHandler, LoginHijack, NewSubmissionHandler, SubmitHandler
from frontend import ui_modules
from backend import GetAllSubmissionsHandler, GetSubmissionHandler, ModifySubmissionHandler, AuthenticationHandler, UnauthenticationHandler, GetUserInfoHandler, GetSubmissionFile, RemoveSubmissionHandler

from utils import directories

paths = [directories.data_directory, directories.template_directory, directories.upload_directory]

settings = {
    "cookie_secret": "test_cookie",
    "login_url": "/login",
    "template_path": os.path.join(directories.template_directory, "bootstrap"),
    "ui_modules": ui_modules,
    "static_path": directories.static_directory,
    "debug": True,
}

class MainHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.redirect("/login")

if __name__ == "__main__":
    for _dir_ in paths:
        if not os.path.exists(_dir_):
            os.makedirs(_dir_)
    app = tornado.web.Application([
                                   (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': os.path.join(directories.static_directory, "EULA.txt")}),
                                   
                                   (r"/", MainHandler),
                                   (r"/submit", SubmitHandler),
                                   (r"/new_submission", NewSubmissionHandler),
                                   (r"/login", LoginHijack),
                                   
                                   (r"/profile", MainProfileHandler),
                                   (r"/profile/submissions", SubmissionsHandler),
                                   
                                   (r"/api/user", GetUserInfoHandler),
                                   (r"/api/authenticate", AuthenticationHandler),
                                   (r"/api/unauthenticate", UnauthenticationHandler),
                                   (r"/api/submission/get_all", GetAllSubmissionsHandler),
                                   (r"/api/submission/([^/]+)", GetSubmissionHandler),
                                   
                                   (r"/api/submission/([^/]+)/update", ModifySubmissionHandler),
                                   (r"/api/submission/([^/]+)/remove", RemoveSubmissionHandler),
                                   (r"/api/submission/([^/]+)/file", GetSubmissionFile),
                                   ],
                                  **settings)
    http_server = tornado.httpserver.HTTPServer(app)
    port = int(os.environ.get("PORT", 5000))
    http_server.listen(port)
    #http_server.listen(80)
    #app.listen(80)
    tornado.ioloop.IOLoop.current().start()
