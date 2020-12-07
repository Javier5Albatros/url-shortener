from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ValidationError, validator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse
from models import User, Url
import redis
from pymongo import MongoClient
import shortuuid
from auth import hash_password, get_current_user, check_password, get_user

app = FastAPI()
r = redis.Redis(host="localhost", port=6379, db=0)
client = MongoClient()
mongodb = client['url_shortener']


@app.post('/users')
async def register(user: User):
    if mongodb.users.find_one({"username": user.username}):
        return {"status": 0, "error": "username already exists"}
    password = hash_password(user.password)
    user = user.dict()
    user['password'] = password
    user = User(**user)
    ret = mongodb.users.insert_one(user.dict(by_alias=True))
    return {"status": 1, "msg": "User succesfully registered", "username": user.username, "id": str(ret.inserted_id)}

@app.get('/users')
async def get_users(user: User = Depends(get_current_user)):
    users = []
    for user in mongodb.users.find():
        user = User(**user)
        delattr(user, 'password')
        users.append(user)
    return {'users': users}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = get_user(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=400, detail="Wrong username")
    user = user_dict
    hashed_password = user_dict.password
    if not check_password(form_data.password, hashed_password):
        raise HTTPException(
            status_code=400, detail="Wrong password")
    return {"access_token": user.username, "token-type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.put("/url")
async def save_url(url: str, user: User = Depends(get_current_user)):
    try:
        url = Url(
            url=url,
            url_hash=shortuuid.uuid(name=url, pad_length=10)
        )
        r.set("url:" + url.url_hash, url.url)
        return {"status": 1, "message": "Url succesfully registered", "url": url.url_hash}
    except ValidationError as e:
        return {"status": 0, "error": str(e)}


@app.get("/urls")
async def get_urls(user: User = Depends(get_current_user)):
    urls = {}
    keys = r.keys("*url:*")
    if(not keys):
        return {'status': 0, "message": "There are no urls"}

    for i, key in enumerate(keys):
        key = key.decode("utf-8")
        value = r.get(key)
        value = value.decode("utf-8")
        url_hash = key[4:]
        try:
            url = Url(
                url=value,
                url_hash=url_hash
            )
            urls[i] = url.dict()
        except ValidationError as e:
            return {"status": 0, "error": str(e)}
    return urls


@app.get("/{url_hash}")
async def redirect(url_hash: str):
    url = r.get("url:"+url_hash)
    if(url):
        return RedirectResponse(url=url.decode("utf-8"))
    else:
        return {"status": 0, "message": "Url not found"}
