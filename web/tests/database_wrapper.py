from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, PickleType, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Date, Enum

engine = create_engine('sqlite:///test.db', echo=True)
SQLBase = declarative_base(bind=engine)

class Account(SQLBase):
    __tablename__ = 'accounts'
    name = Column(UnicodeText, primary_key=True)
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
    submitted_date = Column(String)
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
        
        
def check_bound(func):
    
    def _check_bound(cls, *args, **kwargs):
        if not cls._DatabaseWrapper__bound:
            cls.bind()
        return func(cls, *args, **kwargs)
    
    return _check_bound


class DatabaseWrapper:
    __bound = False
    
    @classmethod
    def bind(cls):
        if not cls.__bound:
            SQLBase.metadata.create_all()

            _Session = sessionmaker(bind=engine)
            cls.__session = _Session()
    
    @classmethod
    @check_bound
    def user_in_database(cls, user):
        return bool(cls.__session.query(Account).filter(Account.name == user).first())
    
    @classmethod
    @check_bound
    def submission_in_database(cls, submission_id):
        return bool(cls.__session.query(Submission).filter(Submission.id == submission_id).first())
    
    @classmethod
    @check_bound
    def add_submission(cls, name, sid, data):
        if cls.submission_in_database(sid):
            raise Exception()
        
        submission = Submission(sid, data["title"], data["date"], data["options"])
        cls.__session.add(submission)
        #cls.__session.commit()
        if cls.user_in_database(name):
            account = cls.__session.query(Account).filter(Account.name==name).first()
            account.submissions.append(submission.id)
        else:
            account = Account(name, [submission.id,])
            cls.__session.add(account)
        cls.__session.commit()
        
        
full_test_var = {
                 "date": "November 10, 2016 at 10:11 PM",
                 "status": "submission-pending",
                 "prority": 1,
                 "assignment": {},
                 "options": {
                             "detail_name": "custom",
                             "rafts": False,
                             "color": "white",
                             "infill": 65,
                             "supports": True,
                             "detail_height": 0.15
                },
                "title": "Full Test"
                }

DatabaseWrapper.bind()
print DatabaseWrapper.user_in_database("benjamingothard")
print DatabaseWrapper.submission_in_database("9237227f-5399-48b1-a666-5c836d7130f3")
print "Before: {}".format(DatabaseWrapper.submission_in_database("18b6e976-a890-4412-8005-b8e728efa7df"))
DatabaseWrapper.add_submission("Full Test", "18b6e976-a890-4412-8005-b8e728efa7df", full_test_var)
print "After: {}".format(DatabaseWrapper.submission_in_database("18b6e976-a890-4412-8005-b8e728efa7df"))
