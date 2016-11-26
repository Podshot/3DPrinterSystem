import tornado.web
from utils import SQLWrapper
import requests
import random
from frontend.profile import LoginHijack
import json

class AuthenticatedHandlerBase(tornado.web.RequestHandler):
    _auths = {}
    
    def __init__(self, application, request, **kwargs):
        super(AuthenticatedHandlerBase, self).__init__(application, request, **kwargs)
    
    def push(self, ip):
        if ip in self._auths.values():
            self.pop_by_ip(ip)
        a_id = random.randint(0, 1000)
        self.__class__._auths[a_id] = ip
        print self._auths
        return a_id
        
    def pop_by_ip(self, ip):
        for (key, value) in self.__class__._auths.items():
            if value == ip:
                del self.__class__._auths[key]
                break
    
    def pop_by_id(self, aid):
        if aid in self.__class__._auths:
            del self.__class__._auths[aid]
        
    def is_authenticated(self, ip, aid=-1):
        print "Result: {}".format((self.__class__._auths.get(int(aid), '0.0.0.0') == ip))
        return (self.__class__._auths.get(int(aid), '0.0.0.0') == ip)
    
    def api_authenticated(self):
        auth_id = -1
        ip = (self.request.remote_ip if 'X-Forwarded-For' not in self.request.headers else self.request.headers['X-Forwarded-For'])
        if self.request.method.upper() == "POST" and self.request.headers.get("Content-Type") == "application/json":
            payload = json.loads(self.request.body.decode('utf-8'))
            auth_id = payload.get("auth_id", -1)
            setattr(self.request, "json", payload)
        else:
            auth_id = self.get_argument("auth_id", default=-1)
        print "================="
        print "IP: {}".format(ip)
        print "ID: {}".format(auth_id)
        print "Headers: {}".format(self.request.headers['X-Forwarded-For'])
        print "Auths: {}".format(self.__class__._auths)
        print "================="
        if self.is_authenticated(ip, auth_id):
            return True
        else:
            self.set_status(405)
            self.set_header("Content-Type", "application/json")
            self.write({"error": "Invalid authentication ID"})
            self.flush()
        return False
        

class AuthenticationHandler(AuthenticatedHandlerBase):
    
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        login = {
             "school": 1765201,
             "username": username,
             "password": password
            }
        response = requests.post("http://schoologyauth.foresthills.edu/userAuth.php", data=login)
        if LoginHijack._login_successful(response):
            account = SQLWrapper.get_account(username)
            if account.is_admin:
                a_id = self.push(self.request.remote_ip if 'X-Forwarded-For' not in self.request.headers else self.request.headers['X-Forwarded-For'])
                self.set_header("Content-Type", "application/json")
                self.write({"auth_id": a_id})
            else:
                self.set_header("Content-Type", "application/json")
                self.write({"auth_id": -1})
        else:
            self.set_header("Content-Type", "application/json")
            self.write({"auth_id": -1})
        self.flush()
                
                
class GetAllSubmissionsHandler(AuthenticatedHandlerBase):
    
    def get(self):
        if self.api_authenticated():
            parameters = self.get_argument("with_data", default=False)
            self.set_header("Content-Type", "application/json")
            if parameters:
                submissions = []
                for sid in SQLWrapper.get_all_submissions():
                    sub_data = {sid.id: sid.data}
                    print sub_data
                    submissions.append(sub_data)
                self.write({"submissions": submissions})
            else:
                self.write({"submissions": [sid.id for sid in SQLWrapper.get_all_submissions()]})
            self.flush()
        
class GetSubmissionHandler(AuthenticatedHandlerBase):
    
    def get(self):
        if self.api_authenticated():
            submission_id = self.get_argument("submission")
            self.set_header("Content-Type", "application/json")
            self.write(SQLWrapper.get_submission(submission_id).data)
            self.flush()
        
class ModifySubmissionHandler(AuthenticatedHandlerBase):
    
    def post(self): #TODO: Add authentication
        if self.api_authenticated():
            payload = self.request.json
            submission_id = payload["submission"]
            data = payload["data"]
            if SQLWrapper.has_been_submitted(submission_id):
                SQLWrapper.update_submission(submission_id, data)
                self.set_header("Content-Type", "application/json")
                self.write({"result": 1})
                self.flush()
            else:
                self.set_header("Content-Type", "application/json")
                self.write({"result": -1})
                self.flush()
        