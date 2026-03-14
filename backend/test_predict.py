import requests
import json

url = 'http://127.0.0.1:5001'

print("--- Registering ---")
res = requests.post(f'{url}/register', json={'username': 'testuserimg', 'email': 'testimg@test.com', 'password': 'Password1'})
print(res.status_code, res.text)

print("\n--- Logging in ---")
res = requests.post(f'{url}/login', json={'username': 'testuserimg', 'password': 'Password1'})
print(res.status_code, res.text)
token = res.json().get('access_token')

print(f"\n--- Predicting ---")
headers = {'Authorization': f'Bearer {token}'}
# Use app.py as the file to test the type validation
with open('app.py', 'rb') as f:
    files = {'image': ('app.py', f, 'image/jpeg')}
    res_pred = requests.post(f'{url}/predict', headers=headers, files=files)
print(res_pred.status_code, res_pred.text)

print("\n--- Sending OPTIONS ---")
res_opt = requests.options(f'{url}/predict')
print(res_opt.status_code, dict(res_opt.headers))
