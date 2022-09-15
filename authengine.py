import datetime
import bcrypt

import database


logins = database.Database("data/logins.json")


def bytestr(s) -> str:
	return str(s)[2:-1]


def hash_to_urlsafe(s: str) -> str:
	return s.replace("/", "_").replace("$", "-")


def login(username: str, password: str) -> str | bool:
	user = logins.get(username)
	if not user:
		return False
	salt = user["salt"]
	hashed = bytestr(bcrypt.hashpw(password.encode("utf-8"), bytes(salt, "utf-8")))
	if hashed != user["password"]:
		return False
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


def register(username: str, password: str) -> bool | str:
	if logins.get(username):
		return "A user with that name already exists."
	if len(username) < 3:
		return "Username must be at least 3 characters long."
	if len(password) < 8:
		return "Password must be at least 8 characters long."
	if not any(char.isdigit() for char in password):
		return "Password must contain at least one digit."
	if not any(char.isupper() for char in password):
		return "Password must contain at least one uppercase letter."
	salt = bcrypt.gensalt()
	hashed = str(bcrypt.hashpw(password.encode("utf-8"), salt))
	logins.post(username, {
		"password": bytestr(hashed),
		"salt": bytestr(salt),
		"token": None,
		"expires": None,
		"level": 0
	})
	return True
