import urllib.request, urllib.error, json

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/auth/register', 
    data=json.dumps({'name':'Test','email':'test@test.com','password':'pass'}).encode(), 
    headers={'Content-Type': 'application/json'}
)
try:
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(e.read().decode())
