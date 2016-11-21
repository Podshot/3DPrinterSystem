from utils import SQLWrapper
"""
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, PickleType, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Date, Enum
from datetime import datetime
"""
"""
engine = create_engine('sqlite:///test.db', echo=False)
#engine = create_engine('sqlite:///:memory:', echo=True)
SQLBase = declarative_base(bind=engine)


class Account(SQLBase):
    __tablename__ = 'accounts'
    name = Column(String, primary_key=True)
    submissions = Column(PickleType)
    is_admin = Column(Boolean)
    is_robotics = Column(Boolean)
    
    def __init__(self, name, submissions, is_admin=False, is_robotics=False):
        self.name = name
        self.submissions = submissions
        self.is_admin = is_admin
        self.is_robotics = is_robotics
        
class Submission(SQLBase):
    __tablename__ = 'submissions'
    
    id = Column(String(36), primary_key=True)
    name = Column(UnicodeText)
    submitted_date = Column(Date)
    priority = Column(Integer)
    status = Column(Enum('pending', 'denied', 'completed'))
    options = Column(PickleType)
    assignment = Column(PickleType)
    
    def __init__(self, _id, name, submitted_date, options, assignment=None, priority=1, status='pending'):
        self.id = _id
        self.name = name
        self.submitted_date = submitted_date
        self.options = options
        if assignment:
            self.assignment = assignment
        else:
            self.assignment = {}
        self.priority = priority
        self.status = status

SQLBase.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
s = Session()

if not bool(s.query(Account).filter(Account.name=='benjamingothard').first()):
    print "Doesn't exist in database!"
    account = Account("benjamingothard", [], is_admin=True)
    sub = Submission(
                     "9237227f-5399-48b1-a666-5c836d7130f3", 
                     "SQL Test Submission", 
                     datetime.now(),
                     {
                      "detail_name": "high",
                      "rafts": True,
                      "color": "red",
                      "infill": 10,
                      "supports": False,
                      "detail_height": 0.1
                      })
    account.submissions.append(sub.id)
    s.add_all([account, sub])
    s.commit()
else:
    print "Does exist in database!"
    var = s.query(Account).filter(Account.name == 'benjamingothard')
    print "var: {}".format([a.name for a in var])
    print "=================="
    for user in s.query(Account):
        print "{}, {}, \"{}\"".format(type(user), user.name, user.submissions[0])
        #print user.submissions[0].options["infill"]
    print "+++++++++++++++++++++"
    #subq = s.query(Account, Submission).join(Account.name).with_labels().subquery()
    #print ":" + sub1
    for sub in s.query(Submission):
        sub = s.query(Submission).filter(Submission.id == '9237227f-5399-48b1-a666-5c836d7130f3').first()
        #print "{}, {}".format(sub.name, sub.id)
        for attr in sub.__dict__:
            print "    {}: {}".format(attr, getattr(sub, attr))
        
s.close()
"""

test_sub = {
            "status": "pending",
            "title": "Full Test",
            "assignment": {},
            "priority": 1,
            "date": "November 10, 2016 at 10:11 PM",
            "options": {
                        "detail_name": "custom",
                        "rafts": False,
                        "color": "white",
                        "infill": 65,
                        "supports": True,
                        "detail_height": 0.15
                        }
            }

#try:
#    SQLWrapper.add_submission("18b6e976-a890-4412-8005-b8e728efa7df", "benjamingothard", test_sub)
#except SQLWrapper.SubmissionAlreadyExistsException:
#    pass

#print SQLWrapper.get_submission("18b6e976-a890-4412-8005-b8e728efa7df").data["title"]
print SQLWrapper.get_all_submissions_by_user('benjamingothard')
print SQLWrapper.get_all_submissions()
print SQLWrapper.get_account("benjamingothard").name