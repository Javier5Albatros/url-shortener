from fastapi import Depends
from pydantic import ValidationError
import shortuuid
from fastapi import APIRouter
from starlette.responses import RedirectResponse
from app.models.url import Url
from app.models.user import User
from app.services.auth import get_current_user
from app.db.mongo import mongodb as mongo


router = APIRouter()


@router.put("/url")
async def save_url(url: str, user: User = Depends(get_current_user)):
    try:
        url = Url(
            url=url,
            url_hash=shortuuid.uuid(name=url, pad_length=10)
        )
        if mongo.urls.find_one({"url_hash": url.url_hash}):
            return {"status": 0, "message": "Url already registered"}
        else:
            mongo.urls.insert(url.dict())
        return {"status": 1, "message": "Url succesfully registered", "url": url.url_hash}
    except ValidationError as e:
        return {"status": 0, "error": str(e)}


@router.get("/urls")
async def get_urls(user: User = Depends(get_current_user)):
    urls = {}

    for url in mongo.urls.find():
        urls[url["url"]] = url["url_hash"]
    return urls


@router.get("/{url_hash}")
async def redirect(url_hash: str, user: User = Depends(get_current_user)):
    url = mongo.urls.find_one({"url_hash": url_hash})
    if url:
        return RedirectResponse(url=url.decode("utf-8"))
    else:
        return {"status": 0, "message": "Url not found"}
