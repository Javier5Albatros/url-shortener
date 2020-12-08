from pydantic import BaseModel, validator
import re


class Url(BaseModel):
    url: str
    url_hash: str

    @validator('url', pre=True)
    def is_url(self, v):
        if not re.match(url_regex, v):
            raise ValueError('Malformed URL: ' + v)
        return v


url_regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
