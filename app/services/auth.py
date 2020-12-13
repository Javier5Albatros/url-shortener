from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import bcrypt
from app.db.mongo import mongodb
from app.models.user import User
from app.models.token import TokenData, Token
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "acd919cd44a7ecd00799de9b27d1dfb18a7c8a7f3609135783289fc5b50c1d1"
ALGORITHM = "HS256"
ACCES_TOKEN_EXPIRE_MINUTES = 3600


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


def autheticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not check_password(password, user.password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
