import requests
import gzip

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

sub = all_response.json()['submissions'][0]

certain_payload = {
                   "auth_id": auth_id
                   }

certain_response = requests.get('http://{}/api/submission/{}'.format(ip, sub), data=certain_payload)

print certain_response.json()
print certain_response.json()['title']

update_payload = {
                  #'submission': '18dfcd3d-74dd-472b-9700-1d4e221a31f7',
                  'auth_id': auth_id,
                  'data': {
                           'status': change_status
                           }
                  }

update_response = requests.post('http://{}/api/submission/{}/update'.format(ip, sub), json=update_payload)

print update_response.json()

certain_response_2 = requests.get('http://{}/api/submission/{}'.format(ip, sub), data=certain_payload)
print certain_response_2.json()


r = requests.get("http://{}/api/submission/{}/file".format(ip, sub), stream=True)
with open("{}.stl.gz".format(sub), 'wb') as f:
    for chunk in r.iter_content(chunk_size=1024): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
with gzip.open("{}.stl.gz".format(sub), 'rb') as f:
    content = f.read()
    with open("{}.stl".format(sub), 'wb') as out:
        out.write(content)