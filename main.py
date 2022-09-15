from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse, JSONResponse
import asyncio
import uvicorn

import authengine
import database

app = FastAPI(docs_url=None)
db = database.Database()


@app.get("/")
def root() -> PlainTextResponse:
    return PlainTextResponse("[200] API is running correctly.", 200)


@app.get("/get/{username}/{token}")
def get_database_entry(username: str, token: str) -> JSONResponse:
    print(f"GET /get/{username}/{token}")
    if authengine.is_user_logged_in(username, token):
        print(db.get(username))
        return JSONResponse(db.get(username), 200)
    return JSONResponse({"error": "Unauthorised."}, 401)


class AuthSchema(BaseModel):
    username: str
    token: str


class RegisterSchema(BaseModel):
    username: str
    token: str
    new_username: str
    new_password: str


@app.post("/register")
def register(data: RegisterSchema) -> JSONResponse:
    try:
        auth = authengine.register(data.username, data.token, data.new_username, data.new_password)
        token = authengine.login(data.new_username, data.password)
        return JSONResponse({"success": "User registered.", "token": token}, 200)
    except authengine.Error as e:
        return JSONResponse({"error": auth.message or "Something went wrong"}, 409)


@app.post("/login")
def login(data: AuthSchema):
    try:
        token = authengine.login(data.username, data.token)
        return JSONResponse({"token": token}, 200)
    except authengine.Error as e:
        return JSONResponse({"error": "Incorrect username or password."}, 401)


config = uvicorn.Config(app, host="0.0.0.0", port=10000, lifespan="on", access_log=False, log_level="debug")
server = uvicorn.Server(config)
server.config.setup_event_loop()
loop = asyncio.new_event_loop()
loop.run_until_complete(server.serve())
