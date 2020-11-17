from typing import Optional
from fastapi import FastAPI
import redis
import re

app = FastAPI()
r = redis.Redis(host="localhost", port=6379, db=0)

url_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

@app.put("/url")
async def save_url(url: str):
    if(not re.match(url_regex, url)):
        return {"status": 0, "message": "Malformed url"}
    else:
        if(r.get(url)):
            return {"status": 0, "message": "Url already registered"}
        else:
            r.set(url, url)
            return {"status": 1, "message": "Url succesfully registered"}
