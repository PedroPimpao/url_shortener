from pydantic import BaseModel

class UserSchema(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
            from_attributes = True

class URLSchema(BaseModel):
    title: str
    original_url: str

    class Config:
            from_attributes = True

class ShortedURLSchema(BaseModel):
    short_url: str

    class Config:
            from_attributes = True
