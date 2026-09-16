from typing import Optional

from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_admin: Optional[str] = None


class UserUpdate(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr


class UserList(BaseModel):
    users: list[UserPublic]


class UpdateAdmin(BaseModel):
    username: str
    credencial: str


class AdminPublic(UserPublic):
    is_admin: bool


class Token(BaseModel):
    access_token: str
    token_type: str
