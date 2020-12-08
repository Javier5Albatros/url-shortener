from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import bcrypt
from app.main import mongodb
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('UTF-8'), salt)


def check_password(password: str, hashed: str):
    password = password.encode('UTF-8')
    return bcrypt.checkpw(password, hashed.encode('UTF-8'))


def get_user(username: str):
    user = mongodb.users.find_one({"username": username})
    if user:
        return User(**user)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = get_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWWW-Authenticate": "Bearer"},
        )
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive User")

    return user
