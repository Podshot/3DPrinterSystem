import requests

connection_pointer = "printer-system-test.herokuapp.com"

login_payload = {
                 }

auth_id = login_response = requests.post("http://{}/api/authenticate".format(connection_pointer), data=login_payload)
if login_response.status_code == 405:
    auth_id = -1
else:
    auth_id = login_response.json()['auth_id']

def get_all_submissions():
    all_response = requests.get("http://{}/api/submission/get_all".format(connection_pointer), data={'auth_id': auth_id, 'with_data': True})
    if all_response.status_code == 405:
        return []
    else:
        return all_response.json()['submissions']
    