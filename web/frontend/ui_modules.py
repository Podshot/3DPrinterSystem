import tornado.web
import copy
from utils import directories
import os
    
class Submission(tornado.web.UIModule):
    
    def embedded_css(self):
        return """
        .submission-pending {
        border: 4px solid black; 
        border-radius: 5px; 
        background-color: lightgrey;
        margin-left: 5px;
        }
        .submission-completed {
        border: 4px solid green; 
        border-radius: 5px; 
        background-color: lightgrey;
        margin-left: 5px;
        }
        .submission-denied {
        border: 4px solid red; 
        border-radius: 5px; 
        background-color: lightgrey;
        margin-left: 5px;
        }
        p.content {
        margin-left: 5px;
        margin-top: 5px;
        }
        p.job_details {
        margin-top: -10px;
        margin-bottom: -10px;
        margin-left: 20px;
        }
        p.class_details {
        margin-left: 30px;
        }
        h4.assignment_header {
        margin-top: 15px;
        margin-left: 20px;
        margin-bottom: -10px;
        }
        a.actions {
        margin-left: 15px;
        }
        """
    
    def render(self, sub):
        entry = copy.deepcopy(sub.data)
        entry["sub_id"] = sub.id
        return self.render_string(os.path.join(directories.template_directory, "bootstrap","modules", "submission_entry.html"), **entry)
