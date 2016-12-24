import tornado.web
import copy
from utils import directories  # @UnresolvedImport
import os

status_map = {
              "pending": "default",
              "completed": "success",
              "denied": "danger",
              }
    
class Submission(tornado.web.UIModule):
    
    def render(self, sub):
        entry = copy.deepcopy(sub.data)
        entry["sub_id"] = sub.id
        entry["status"] = status_map[entry["status"]]
        return self.render_string(os.path.join(directories.template_directory, "bootstrap","modules", "submission_entry.html"), **entry)
    
class Navbar(tornado.web.UIModule):
    
    def render(self, page, logged_in=True):
        return self.render_string("navbar.html", page=page, logged_in=logged_in, version=0.75)
