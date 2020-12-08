from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, APIRouter, HTTPException
from app.models.user import User
from app.auth import get_current_user, get_user, hash_password, check_password
from app.main import mongodb

router = APIRouter()


@router.post('/users')
async def register(user: User):
    if mongodb.users.find_one({"username": user.username}):
        return {"status": 0, "error": "username already exists"}
    password = hash_password(user.password)
    user = user.dict()
    user['password'] = password
    user = User(**user)
    ret = mongodb.users.insert_one(user.dict(by_alias=True))
    return {"status": 1, "msg": "User succesfully registered", "username": user.username, "id": str(ret.inserted_id)}


@router.get('/users')
async def get_users(user: User = Depends(get_current_user)):
    users = []
    for user in mongodb.users.find():
        user = User(**user)
        delattr(user, 'password')
        users.append(user)
    return {'users': users}


@router.post("/token")
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


@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
