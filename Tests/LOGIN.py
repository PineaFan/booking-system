import requests

# Make a request to localhost:10000 with post data

username = input("Username: ")
password = input("Password: ")  # Yes, this is insecure, I don't think pycharm terminals support disabling echo

req = requests.post(
    "http://localhost:10000/login",
    json={"username": username, "password": password}
)
print(req.text)
