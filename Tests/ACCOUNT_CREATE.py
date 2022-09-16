import requests

# Make a request to localhost:10000 with post data

admin_username = input("Your username: ")
token = input("Your login token: ")
username = input("Username: ")
password = input("Password: ")  # Yes, this is insecure, I don't think pycharm terminals support disabling echo

req = requests.post(
    "http://localhost:10000/user/register",
    json={
        "new_username": username,
        "new_password": password,
        "username": admin_username,
        "token": token,
        "force": False
    }
)
print(req.text)


"""
Pinea | Admin
new user | testing 
"""