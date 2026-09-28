import requests

response = requests.get("http://localhost:8888/identity/api/auth/login")
print(response.status_code)