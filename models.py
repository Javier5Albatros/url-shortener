from typing import Optional
from pydantic import BaseModel, ValidationError, validator, Field
from regex import url_regex
from bson import ObjectId
import re




class User(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None




class Url(BaseModel):
    url: str
    url_hash: str

    @validator('url', pre=True)
    def is_url(cls, v):
        if(not re.match(url_regex, v)):
            raise ValueError('Malformed URL: '+v)
        return v
