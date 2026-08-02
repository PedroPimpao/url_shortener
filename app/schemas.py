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
    original_url: str

    class Config:
            from_attributes = True

class UpdateTitleSchema(BaseModel):
    title: str

    class Config:
        from_attributes = True

# class URLAccessSchema(BaseModel):
#     short_code: str

#     class Config:
#         from_attributes = True
