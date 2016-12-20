import tornado.web
#from web.backend.accounts import account_handler
import requests
from datetime import datetime
import os
from gzip import GzipFile
import glob
import uuid

import urllib3
urllib3.disable_warnings()

from utils import directories, SQLWrapper, DropboxWrapper

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
        self.render("login.html")
       
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
            print 'Successfully logged in'
            self.set_secure_cookie("user", username)
            #self.set_status(202)
            self.redirect("profile")
        else:
            print "Did not successfully log in"
            self.write("Not logged in")
            self.finish()
    
class MainProfileHandler(BaseProfileHandler):
    
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.render("profile.html", user=name)
        
class NewSubmissionHandler(BaseProfileHandler):
    
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        account = SQLWrapper.get_account(name)
        self.render("new_submission.html", is_robotics=account.is_robotics)
        
class SubmitHandler(BaseProfileHandler):
    detail_map = {"high": 0.1, "normal": 0.2, "low": 0.3}
    
    @tornado.web.authenticated
    def post(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        #print self.get_argument("file")
        info = self.request.files["file"][0]
        filename = info["filename"]
        filename = tornado.web.escape.xhtml_escape(os.path.basename(filename)).replace("$$", "_._")
        self.redirect("profile")
        if filename.lower().endswith(".stl") and info["content_type"] == "application/octet-stream":
            submission_data = {
                               "title": self.get_argument("title"),
                               "date": datetime.strftime(datetime.now(), "%B %d, %Y at %I:%M %p"),
                               "status": "pending",
                               "priority": 1,
                               "options": {
                                           "detail_name": self.get_argument("quality"),
                                           "detail_height": float(self.detail_map.get(self.get_argument("quality"), self.get_argument("custom_quality"))),
                                           "color": self.get_argument("color"),
                                           "rafts": (True if self.get_argument("rafts", default="off") == "on" else False),
                                           "supports": (True if self.get_argument("supports", default="off") == "on" else False),
                                           "infill": int(self.get_argument("infill")),
                                           },
                               "assignment": {},
                               "for_robotics": (True if self.get_argument("for_robotics", default="off") == "on" else False),
                               }
            
            if self.get_argument("assignment", default="off") == "on":
                submission_data["assignment"]["class_name"] = self.get_argument("class_name")
                submission_data['assignment']['teacher'] = self.get_argument('teacher')
                date = self.get_argument('due_date').split("-")
                submission_data['assignment']['due_date'] = "{}-{}-{}".format(date[1], date[2], date[0])
                
            submission_id = str(uuid.uuid4())
            SQLWrapper.add_submission(submission_id, name, submission_data)
            file_path = os.path.join(directories.upload_directory, submission_id)
            
            file_gz_obj = GzipFile(file_path + ".stl.gz", 'wb')
            file_gz_obj.write(info['body'])
            file_gz_obj.close()
            
            with open('{}.stl.gz'.format(file_path), 'rb') as _in:
                DropboxWrapper.add_submission(submission_id, _in.read())
                
            os.remove('{}.stl.gz'.format(file_path))
        
        #print "Content: {}".format(info["body"])
        
class SubmissionsHandler(BaseProfileHandler):
    
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        submissions = SQLWrapper.get_all_submissions_by_user(name)
        sorted_submission_ids = sorted(range(len(submissions)), key=lambda i: datetime.strptime(submissions[i].data["date"], "%B %d, %Y at %I:%M %p"), reverse=True)
        sorted_submissions = [submissions[sid] for sid in sorted_submission_ids]
        
        self.render("submissions.html", ids=sorted_submissions)
