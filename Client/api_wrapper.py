import requests
import gzip

connection_pointer = "printer-system-test.herokuapp.com"
#connection_pointer = "127.0.0.1:5000"

class APIWrapper(object):
    
    def __init__(self, username, password):
        login_payload = {
                 'username': username,
                 'password': password
                 }
        self._username = username
        response = requests.post("http://{}/api/authenticate".format(connection_pointer), data=login_payload).json()
        if response['auth_id'] == -1:
            print "Login failed..."
            self._failed_login = True
        else:
            print "Login succeeded..."
            self._failed_login = False
        self._auth_id = response['auth_id']
        
    def get_username(self):
        return self._username
        
    def login_failed(self):
        return self._failed_login
    
    def get_all_submissions(self):
        all_response = requests.get("http://{}/api/submission/get_all".format(connection_pointer), data={'auth_id': self._auth_id, 'with_data': True})
        if all_response.status_code == 405:
            return []
        else:
            return all_response.json()['submissions']
        
    def get_user(self, username):
        username_response = requests.get("http://{}/api/user".format(connection_pointer), data={"auth_id": self._auth_id, "username": username})
        if username_response.status_code == 405:
            return None
        else:
            return username_response.json()
        
    def download_submitted_file(self, submission_id):
        # NOTE the stream=True parameter
        r = requests.get("http://{}/api/submission/{}/file".format(connection_pointer, submission_id), stream=True)
        with open("{}.stl.gz".format(submission_id), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    
        with gzip.open("{}.stl.gz".format(submission_id), 'rb') as f:
            content = f.read()
            with open("{}.stl".format(submission_id), 'wb') as out:
                out.write(content)
        return "{}.stl.gz".format(submission_id)