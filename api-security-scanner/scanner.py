import requests

login_info = {
    "email":"bubble@gmail.com",
    "password":"Bubble123#"
}

response = requests.post("http://localhost:8888/identity/api/auth/login", json=login_info)
print("POST Login Status Code: " + str(response.status_code))

if response.status_code == 200:
    token = response.json()["token"] # or token = response.json().get("token")
    print("Login Token: " + token)

    headers = {
        "Authorization":"Bearer " + token
    }
    getResponse = requests.get("http://localhost:8888/identity/api/v2/user/dashboard", headers=headers)
    print("GET Dashboard Status Code: " + str(getResponse.status_code))
    print("JSON GET Response: " + str(getResponse.json()))
