import requests

username = raw_input("Username: ")
password = raw_input("Password: ")
change_status = raw_input("Change 'stauts' to (pending/completed/denied): ")

login_payload = {
                 'username': username,
                 'password': password
                 }

login_response = requests.post("http://127.0.0.1/api/authenticate", data=login_payload)
auth_id = login_response.json()['auth_id']

all_response = requests.get("http://127.0.0.1/api/submission/get_all", data={'auth_id': auth_id})

print all_response.json()

certain_payload = {
                   'submission': '18dfcd3d-74dd-472b-9700-1d4e221a31f7',
                   "auth_id": auth_id
                   }

certain_response = requests.get('http://127.0.0.1/api/submission', data=certain_payload)

print certain_response.json()
print certain_response.json()['title']

update_payload = {
                  'submission': '18dfcd3d-74dd-472b-9700-1d4e221a31f7',
                  'auth_id': auth_id,
                  'data': {
                           'status': 'completed'
                           }
                  }

update_response = requests.post('http://127.0.0.1/api/submission/update', json=update_payload)

print update_response.json()

certain_response_2 = requests.get('http://127.0.0.1/api/submission', data=certain_payload)
print certain_response_2.json()