from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, ValidationError, validator
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


class Url(BaseModel):
    url: str
    url_hash: str

    @validator('url', pre=True)
    def is_url(cls, v):
        if(not re.match(url_regex, v)):
            raise ValueError('Malformed URL: '+v)
        return v


@app.put("/url")
async def save_url(url: str):
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
async def get_urls():
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
