from typing import Optional
from fastapi import FastAPI
from starlette.responses import RedirectResponse
import hashlib
import redis
import re
import shortuuid

app = FastAPI()
r = redis.Redis(host="54.37.224.17", port=6379, db=0)

url_regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


@app.put("/url")
async def save_url(url: str):
    if(not re.match(url_regex, url)):
        return {"status": 0, "message": "Malformed url"}
    else:
        url_hashed = shortuuid.uuid(name=url, pad_length=10)
        if(r.get("url:" + url_hashed)):
            return {"status": 0, "message": "Url already registered"}
        else:
            r.set("url:" + url_hashed, url)
            return {"status": 1, "message": "Url succesfully registered", "url": url_hashed}


@app.get("/urls")
async def get_urls():
    urls = r.keys("*url:*")
    if(urls):
        return {"status": 1, "urls": urls}
    else:
        return {"status": 0, "message": "Error fetching the urls"}


@app.get("/{url_hash}")
async def redirect(url_hash: str):
    url = r.get("url:"+url_hash)
    if(url):
        return RedirectResponse(url=url).decode("utf-8")
    else:
        return {"status": 0, "message": "Url not found"}
