from typing import Optional
from fastapi import FastAPI
from starlette.responses import RedirectResponse
import short_url
import redis
import re

app = FastAPI()
r = redis.Redis(host="localhost", port=6379, db=0)

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
        url_hashed = str(url.__hash__())
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
async def redirect(url_hash: int):
    url = r.get("url:"+str(url_hash)).decode("utf-8")
    if(url):
        return RedirectResponse(url=url)
    else:
        return {"status": 0, "message": "Url not found"}
