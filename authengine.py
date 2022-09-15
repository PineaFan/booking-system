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


def login(username: str, password: str) -> str | bool:
    user = logins.get(username)
    if not user:
        raise Error("User does not exist.", 404)
    salt = user["salt"]
    hashed = bytestr(bcrypt.hashpw(password.encode("utf-8"), bytes(salt, "utf-8")))
    if hashed != user["password"]:
        raise Error("Invalid password.", 401)
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


def register(username: str, token: str, new_user: str, password: str) -> bool:
    if not is_user_logged_in(username, token):
        raise Error("You are not logged in.", 401)
    if get_privilege_level(username) < 1:
        raise Error("You do not have permission to do this.", 403)
    if logins.get(new_user):
        raise Error("User already exists.", 409)
    if len(new_user) < 3:
        raise Error("Username must be at least 3 characters long.", 400)
    if len(password) < 8:
        raise Error("Password must be at least 8 characters long.", 400)
    if not any(char.isdigit() for char in password):
        raise Error("Password must contain at least one number.", 400)
    if not any(char.isupper() for char in password):
        raise Error("Password must contain at least one uppercase letter.", 400)
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
