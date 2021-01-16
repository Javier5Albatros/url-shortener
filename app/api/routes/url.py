from fastapi import Depends
from pydantic import ValidationError
import shortuuid
from fastapi import APIRouter
from starlette.responses import RedirectResponse
from app.models.url import UrlInDb
from app.models.user import User
from app.services.auth import get_current_user
from app.db.mongo import mongodb as mongo

router = APIRouter()


@router.put("/url")
async def save_url(url: str, user: User = Depends(get_current_user)):
    try:
        url = UrlInDb(
            url=url,
            url_hash=shortuuid.uuid(name=url, pad_length=10),
            user=user.username
        )
        if mongo.urls.find_one({"url_hash": url.url_hash, "user": user.username}):
            return {"status": 0, "message": "Url already registered"}
        else:
            mongo.urls.insert(url.dict())
        return {"status": 1, "message": "Url succesfully registered", "url": url.url_hash}
    except ValidationError as e:
        return {"status": 0, "error": str(e)}


@router.get("/urls")
async def get_urls(user: User = Depends(get_current_user)):
    urls = {}
    i = 0
    if user.username == "root":
        for url in mongo.urls.find():
            urls[i] = {
                "url": url["url"],
                "url_hash": url["url_hash"],
                "user": url["user"]
            }
            i += 1
    else:
        for url in mongo.urls.find({"user": user.username}):
            urls[url["url"]] = url["url_hash"]
    return urls


@router.get("/{url_hash}")
async def redirect(url_hash: str, user: User = Depends(get_current_user)):
    url = mongo.urls.find_one({"url_hash": url_hash})
    if (url and url["user"] == user.username) or url["user"] == "root":
        return RedirectResponse(url=url["url"])
    else :
        return {"status": 0, "message": "Non authorized url"}
    return {"status": 0, "message": "Url not found"}
