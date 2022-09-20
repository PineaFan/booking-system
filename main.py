import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel

import authengine
import bookings
import database

app = FastAPI(docs_url="/docs")
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


@app.patch("/user/password")
def change_password(data: MultiUserData) -> JSONResponse:
    """Lets users change the password of anyone a lower level than them, or themselves."""
    action = authengine.change_password(data.auth_username, data.auth_token, data.username, data.password)
    if isinstance(action, authengine.Error):
        return JSONResponse(
            {"message": action.message or "Something went wrong", "satus_code": action.code},
            action.code
        )
    return JSONResponse({"message": "Password changed.", "satus_code": 200}, 200)


class BookingData(BaseModel):
    auth_username: str
    auth_token: str
    username: str | None = None
    booking_id: str | None = None
    # booking: bookings.BookingSchema | None = None


@app.get("/bookings")
def get_bookings(data: BookingData) -> JSONResponse:
    """
        Gets a booking by its id, or all if no id is provided.
        Users can get the bookings of themselves, and anyone of a lower level.
    """
    action = bookings.get_bookings(data.auth_username, data.auth_token, data.username, data.booking_id)
    if isinstance(action, bookings.Error):
        return JSONResponse(
            {"message": action.message or "Something went wrong", "satus_code": action.code},
            action.code
        )
    return JSONResponse({"message": "Bookings retrieved.", "bookings": action, "satus_code": 200}, 200)


@app.post("/bookings")
def add_booking(data: BasicData) -> JSONResponse:
    pass


@app.delete("/bookings")
def delete_booking(data: BasicData) -> JSONResponse:
    pass


@app.patch("/bookings")
def modify_booking(data: BasicData) -> JSONResponse:
    pass


config = uvicorn.Config(app, host="0.0.0.0", port=10000, lifespan="on", access_log=False, log_level="trace")
server = uvicorn.Server(config)
server.config.setup_event_loop()
loop = asyncio.new_event_loop()
loop.run_until_complete(server.serve())
