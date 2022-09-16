from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse, JSONResponse
import asyncio
import uvicorn

import authengine
import database

app = FastAPI(docs_url="/docs", redoc_url="/redoc")
db = database.Database()


@app.get("/")
def root() -> PlainTextResponse:
    """Returns 200 OK."""
    return PlainTextResponse("[200] API is running correctly.", 200)


class BasicData(BaseModel):
    username: str
    token: str


class LoginData(BaseModel):
    username: str
    password: str


class MultiUserData(BaseModel):
    auth_username: str
    auth_token: str
    username: str
    password: str | None = None
    force: bool | None = None


@app.post("/user/get")
def get_database_entry(data: MultiUserData) -> JSONResponse:
    """Gets user data of anyone with a lower level than you, or yourself."""
    if authengine.is_user_logged_in(data.auth_username, data.auth_token):
        if authengine.get_privilege_level(data.auth_username) > authengine.get_privilege_level(data.username) or \
                data.auth_username == data.username:
            print(db.get(data.username))
            return JSONResponse(db.get(data.username), 200)
        return JSONResponse({"message": "You do not have permission to view this user's data.", "satus_code": 403}, 403)
    return JSONResponse({"message": "Unauthorised.", "status_code": 401}, 401)


@app.post("/user/register")
def register(data: MultiUserData) -> JSONResponse:
    """
    Creates a new user account at the lowest level.
    """
    auth = authengine.register(data.auth_username, data.auth_token, data.username, data.password, data.force)
    if isinstance(auth, authengine.Error):
        return JSONResponse({"message": auth.message or "Something went wrong", "satus_code": 409}, 409)
    token = authengine.login(data.username, data.password)
    if isinstance(token, authengine.Error):
        return JSONResponse({"message": token.message or "Something went wrong", "satus_code": 409}, 409)
    return JSONResponse({"message": "User registered.", "token": token, "satus_code": 200}, 200)


@app.post("/user/login")
def login(data: LoginData) -> JSONResponse:
    """
    Gives a token to the user if they provide a username and password.
    No other endpoint uses the password for authorisation.
    """
    action = authengine.login(data.username, data.password)
    if isinstance(action, authengine.Error):
        return JSONResponse(
            {"message": action.message or "Something went wrong", "satus_code": action.code},
            action.code
        )
    return JSONResponse({"message": "Logged in", "token": action, "satus_code": 200}, 200)


@app.post("/user/logout")
def logout(data: BasicData):
    """Logs out a user by deleting their auth token and expiry date."""
    action = authengine.logout(data.username, data.token)
    if isinstance(action, authengine.Error):
        return JSONResponse(
            {"message": action.message or "Something went wrong", "satus_code": action.code},
            action.code
        )
    return JSONResponse({"message": "User logged out.", "satus_code": 200}, 200)


@app.delete("/user/delete")
def delete(data: MultiUserData) -> JSONResponse:
    """Lets users delete the accounts of anyone a lower level than them."""
    action = authengine.delete(data.auth_username, data.auth_token, data.username)
    if isinstance(action, authengine.Error):
        return JSONResponse(
            {"message": action.message or "Something went wrong", "satus_code": action.code},
            action.code
        )
    return JSONResponse({"message": "User deleted.", "satus_code": 200}, 200)


config = uvicorn.Config(app, host="0.0.0.0", port=10000, lifespan="on", access_log=False, log_level="trace")
server = uvicorn.Server(config)
server.config.setup_event_loop()
loop = asyncio.new_event_loop()
loop.run_until_complete(server.serve())
