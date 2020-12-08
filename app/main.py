from fastapi import FastAPI
import redis
from pymongo import MongoClient
from app.routes import auth, url

app = FastAPI()
r = redis.Redis(host="localhost", port=6379, db=0)
client = MongoClient()
mongodb = client['url_shortener']

app.include_router(auth.router)
app.include_router(url.router)
