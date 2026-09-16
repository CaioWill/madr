from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr


class Keyadmin(BaseModel):
    key: str


class UpdateAdmin(BaseModel):
    username: str
    credencial: str


class AdminPublic(UserPublic):
    is_admin: bool


class UserList(BaseModel):
    users: list[AdminPublic]


class Token(BaseModel):
    access_token: str
    token_type: str
