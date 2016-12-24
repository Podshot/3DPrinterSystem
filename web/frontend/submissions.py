import tornado.web
from profile import BaseProfileHandler
from utils import SQLWrapper, directories, DropboxWrapper  # @UnresolvedImport
import os
from datetime import datetime
import uuid
from gzip import GzipFile


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