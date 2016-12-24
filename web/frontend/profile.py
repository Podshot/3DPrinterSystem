import tornado.web
import requests
from datetime import datetime

import urllib3
urllib3.disable_warnings()

from utils import SQLWrapper# @UnresolvedImport

class BaseProfileHandler(tornado.web.RequestHandler):
    
    def get_current_user(self):
        return self.get_secure_cookie("user")
    
class LoginHijack(BaseProfileHandler):
    
    @classmethod
    def _login_successful(cls, data):
        history = True
        for entry in data.history:
                history |= (entry.status_code == 302)
        
        return (history and (data.url == "https://app.schoology.com/home"))
    
    def get(self):
        _failed = bool(int(self.get_argument("f", 0)))
        self.render("login.html", failed=_failed)
       
    @tornado.web.asynchronous 
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        login = {
                 "school": 1765201,
                 "username": username,
                 "password": password
                 }
        response = requests.post("http://schoologyauth.foresthills.edu/userAuth.php", verify=False, data=login)
        if self._login_successful(response):
            self.set_secure_cookie("user", username)
            self.redirect("profile")
        else:
            self.redirect("login?f=1")
    
class LandingHandler(BaseProfileHandler):
    
    @tornado.web.authenticated
    def get(self):
        self.render("logged_in_landing.html")
        
class SubmissionsHandler(BaseProfileHandler):
    
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        submissions = SQLWrapper.get_all_submissions_by_user(name)
        sorted_submission_ids = sorted(range(len(submissions)), key=lambda i: datetime.strptime(submissions[i].data["date"], "%B %d, %Y at %I:%M %p"), reverse=True)
        sorted_submissions = [submissions[sid] for sid in sorted_submission_ids]
        
        self.render("submissions.html", ids=sorted_submissions)
