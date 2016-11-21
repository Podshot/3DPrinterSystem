from sqlalchemy import Column, String, PickleType, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import atexit
from sqlalchemy.exc import IntegrityError  
import json
from sqlalchemy.sql.sqltypes import Text
import copy
import directories
import os

engine_path = os.path.join(directories.data_directory, "test.db").replace("\\", "/").replace("C:/", "sqlite:////")
#_engine = create_engine('sqlite:////Users/Ben/Dropbox/3DPrinter/3DPrinter/data/test.db', echo=False)
_engine = create_engine(engine_path)
SQLBase = declarative_base(bind=_engine)

fp = open(os.path.join(directories.data_directory, 'accounts.json'))
account_info = json.load(fp)
fp.close()

class TextPickleType(PickleType):
    impl = Text

class Account(SQLBase):
    __tablename__ = 'accounts'
    name = Column(String, primary_key=True)
    submissions = Column(PickleType)
    is_admin = Column(Boolean)
    is_robotics = Column(Boolean)
    
    def __init__(self, name, submissions=None, is_admin=False, is_robotics=False):
        self.name = name
        if submissions:
            self.submissions = submissions
        else:
            self.submissions = []
        self.is_admin = is_admin
        self.is_robotics = is_robotics
        
class Submission(SQLBase):
    __tablename__ = 'submissions'
    
    id = Column(String(36), primary_key=True)
    data = Column(TextPickleType(pickler=json))
    author = Column(String)
    
    def __init__(self, _id, author, data):
        self.id = _id
        self.author = author
        self.data = data
        
SQLBase.metadata.create_all(_engine)

Session = sessionmaker(bind=_engine)
s = Session()

def _close_session(session):
    session.close()
    
atexit.register(_close_session, s)

def is_in_database(obj, attr, value):
    '''
    Checks to see if a certain entry is currently in the database
    :param obj: The entry type that should be queried
    :param attr: The identifying attribute of the entry type to determine if something matches
    :param value: The value of the attribute to check against
    :rtype: bool
    '''
    return bool(s.query(obj).filter(getattr(obj, attr) == value).first())


def get_account(author, add=True):
    if is_in_database(Account, 'name', author):
        return s.query(Account).filter(Account.name == author).first()
    else:
        account = Account(author, is_admin=(author in account_info["admins"]), is_robotics=(author in account_info["robotics_team"]))
        if add:
            s.add(account)
            s.commit()
        return account


class SubmissionAlreadyExistsException(Exception):
    pass


def add_submission(submission_id, author, data):
    if isinstance(author, (str, unicode)):
        account = get_account(author, add=False)
    elif isinstance(author, Account):
        account = author
    submission = Submission(
                            submission_id,
                            author, 
                            data)
    account.submissions.append(submission_id)
    s.add_all([account, submission])
    try:
        s.commit()
    except IntegrityError:
        s.rollback()
        raise SubmissionAlreadyExistsException()
    
def get_submission(submission_id):
    if is_in_database(Submission, 'id', submission_id):
        return s.query(Submission).filter(Submission.id == submission_id).first()
    else:
        return None

def get_all_submissions():
    return s.query(Submission).all()

def get_all_submissions_by_user(name):
    submissions = s.query(Submission).filter(Submission.author == name).all()
    return submissions

def delete_submission(submission_id):
    s.query(Submission).filter(Submission.id == submission_id).delete()
    s.commit()
    
def has_been_submitted(submission_id):
    return is_in_database(Submission, 'id', submission_id)

def update_submission(submission_id, data):
    submission = get_submission(submission_id)
    
    new_data = copy.deepcopy(submission.data)
    new_data.update(data)
    
    s.query(Submission).filter(Submission.id == submission_id).update({'data': new_data})
    s.flush()
    s.commit()
    
    
if __name__ != '__main__':
    for account in s.query(Account).all():
        account.is_robotics = (account.name in account_info['robotics_team'])
        account.is_admin = (account.name in account_info['admins'])


