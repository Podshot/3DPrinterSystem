import tornado.web  # @UnusedImport
import tornado.ioloop
import tornado.httpserver

from frontend import *  # @UnusedWildImport
from backend import *  # @UnusedWildImport

from utils import directories  # @Reimport

from utils import config

paths = [directories.data_directory, directories.template_directory, directories.upload_directory]

settings = {
    "cookie_secret": os.environ.get("COOKIE"),
    "login_url": "/login",
    "template_path": os.path.join(directories.template_directory, "bootstrap"),
    "ui_modules": ui_modules,
    "static_path": directories.static_directory,
    "debug": True,
}

class MainHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.render("landing.html")

if __name__ == "__main__":
    for _dir_ in paths:
        if not os.path.exists(_dir_):
            os.makedirs(_dir_)
            
    app = tornado.web.Application([
                                   (r"/static/(.*)", tornado.web.StaticFileHandler, { 'path': directories.static_directory }),
                                   
                                   (r"/", MainHandler),
                                   (r"/submit", SubmitHandler),
                                   (r"/new_submission", NewSubmissionHandler),
                                   (r"/login", LoginHijack),
                                   
                                   (r"/landing", LandingHandler),
                                   
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
    port = int(os.environ.get("PORT", 80))
    http_server.listen(port)
    tornado.ioloop.IOLoop.current().start()
