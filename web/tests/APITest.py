import requests

ip = raw_input("Host IP: ")
username = raw_input("Username: ")
password = raw_input("Password: ")
change_status = raw_input("Change 'status' to (pending/completed/denied): ")

login_payload = {
                 'username': username,
                 'password': password
                 }

login_response = requests.post("http://{}/api/authenticate".format(ip), data=login_payload)
auth_id = login_response.json()['auth_id']

all_response = requests.get("http://{}/api/submission/get_all".format(ip), data={'auth_id': auth_id})

print all_response.json()

certain_payload = {
                   'submission': '18dfcd3d-74dd-472b-9700-1d4e221a31f7',
                   "auth_id": auth_id
                   }

certain_response = requests.get('http://{}/api/submission'.format(ip), data=certain_payload)

print certain_response.json()
print certain_response.json()['title']

update_payload = {
                  'submission': '18dfcd3d-74dd-472b-9700-1d4e221a31f7',
                  'auth_id': auth_id,
                  'data': {
                           'status': change_status
                           }
                  }

update_response = requests.post('http://{}/api/submission/update'.format(ip), json=update_payload)

print update_response.json()

certain_response_2 = requests.get('http://{}/api/submission'.format(ip), data=certain_payload)
print certain_response_2.json()