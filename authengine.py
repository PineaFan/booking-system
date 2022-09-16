import datetime
import bcrypt

import database

logins = database.Database("data/logins.json")


class Error(Exception):
    def __init__(self, message, code=400):
        self.message = message
        self.code = code


def bytestr(s) -> str:
    return str(s)[2:-1]


def hash_to_urlsafe(s: str) -> str:
    return s.replace("/", "_").replace("$", "-")


def is_valid_password(s: str) -> bool | Error:
    if len(s) < 8:
        return Error("Password must be at least 8 characters long.", 400)
    if not any(char.isdigit() for char in s):
        return Error("Password must contain at least one number.", 400)
    if not any(char.isupper() for char in s):
        return Error("Password must contain at least one uppercase letter.", 400)
    return True


def is_user_logged_in(username: str, token: str) -> bool:
    user = logins.get(username)
    expected_token, expires = user["token"], user["expires"]
    if token != expected_token:
        return False
    if not expires:
        return False
    if float(datetime.datetime.timestamp(datetime.datetime.now())) > float(expires):
        user["token"] = None
        user["expires"] = None
        logins.post(username, user)
        return False
    return True


def get_privilege_level(username: str) -> int:
    user = logins.get(username)
    if not user:
        return False
    return user["level"]


def login(username: str, password: str) -> str | bool | Error:
    user = logins.get(username)
    if not user:
        return Error("User does not exist.", 404)
    salt = user["salt"]
    hashed = bytestr(bcrypt.hashpw(password.encode("utf-8"), salt.encode("utf-8")))
    if hashed != user["password"]:
        return Error("Invalid password.", 401)
    if not is_user_logged_in(username, user["token"]):
        token = bytestr(bcrypt.hashpw(
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + username).encode("utf-8"),
            bytes(salt, "utf-8")
        ))
        expires = datetime.datetime.now() + datetime.timedelta(days=7)
        logins.post(username, {
            "password": user["password"],
            "token": hash_to_urlsafe(token),
            "expires": str(datetime.datetime.timestamp(expires)),
            "salt": salt,
            "level": 0
        })
        return hash_to_urlsafe(token)
    return hash_to_urlsafe(user["token"])


def register(username: str, token: str, new_user: str, password: str, force: bool = False) -> bool | Error:
    if not force:
        if not is_user_logged_in(username, token):
            return Error("You are not logged in.", 401)
        if get_privilege_level(username) < 1:
            return Error("You do not have permission to do this.", 403)
        if logins.get(new_user):
            return Error("User already exists.", 409)
        if len(new_user) < 3:
            return Error("Username must be at least 3 characters long.", 400)
        if isinstance(is_valid_password(password), Error):
            return is_valid_password(password)
    salt = bcrypt.gensalt()
    hashed = str(bcrypt.hashpw(password.encode("utf-8"), salt))
    logins.post(new_user, {
        "password": bytestr(hashed),
        "salt": bytestr(salt),
        "token": None,
        "expires": None,
        "level": 0
    })
    return True


def logout(username: str, token: str) -> bool | Error:
    if not is_user_logged_in(username, token):
        return Error("You are not logged in.", 401)
    user = logins.get(username)
    user["token"] = None
    user["expires"] = None
    logins.post(username, user)
    return True


def delete(username: str, token: str, user_to_delete: str) -> bool | Error:
    if not is_user_logged_in(username, token):
        return Error("You are not logged in.", 401)
    if get_privilege_level(username) < 1:
        return Error("You do not have permission to do this.", 403)
    if not logins.get(user_to_delete):
        return Error("User does not exist.", 404)
    logins.delete(user_to_delete)
    return True


def change_password(auth_username: str, auth_token: str, username, password: str) -> bool | Error:
    if not is_user_logged_in(auth_username, auth_token):
        return Error("You are not logged in.", 401)
    if get_privilege_level(auth_username) < get_privilege_level(username) and auth_username != username:
        return Error("You do not have permission to do this.", 403)
    if isinstance(is_valid_password(password), Error):
        return is_valid_password(password)
    user = logins.get(username)
    salt = user["salt"]
    hashed = bytestr(bcrypt.hashpw(password.encode("utf-8"), salt.encode("utf-8")))
    logins.post(username, {
        "password": hashed,
        "salt": salt,
        "token": user["token"],
        "expires": user["expires"],
        "level": user["level"]
    })
    return True


"""
Privilege levels:
0 - User
1 - Admin
2 - sudo
"""
