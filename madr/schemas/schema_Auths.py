from enum import Enum

from pydantic import BaseModel, EmailStr


class Credenciais(Enum):
    adimin = 'Admin'
    user = 'User'


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
    credenciais: Credenciais


class UpdateCredencias(BaseModel):
    username: str
    credenciais: Credenciais


class Token(BaseModel):
    access_token: str
    token_type: str
