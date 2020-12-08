from fastapi import Depends
from pydantic import ValidationError
import shortuuid
from fastapi import APIRouter
from starlette.responses import RedirectResponse
from app.models.url import Url
from app.models.user import User
from app.auth import get_current_user
from app.main import r


router = APIRouter()


@router.put("/url")
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


@router.get("/urls")
async def get_urls(user: User = Depends(get_current_user)):
    urls = {}
    keys = r.keys("*url:*")
    if not keys:
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


@router.get("/{url_hash}")
async def redirect(url_hash: str):
    url = r.get("url:"+url_hash)
    if url:
        return RedirectResponse(url=url.decode("utf-8"))
    else:
        return {"status": 0, "message": "Url not found"}
