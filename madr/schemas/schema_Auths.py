from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    username: str = Field(
        description='Nome do usuário.', examples=['Lucas Azevedo']
    )
    email: EmailStr = Field(
        description='Email da conta.', examples=['lucas@gmail.com']
    )
    password: str = Field(
        description='Senha da conta.', examples=['senha123!']
    )


class UserUpdate(BaseModel):
    username: str = Field(
        description='Nome do usuário.', examples=['Lucas Azevedo']
    )
    password: str = Field(
        description='Senha da conta.', examples=['senha123!']
    )


class UserPublic(BaseModel):
    username: str
    email: EmailStr


class Keyadmin(BaseModel):
    key: str = Field(description='Senha de administrador')


class UpdateAdmin(BaseModel):
    username: str = Field(
        description='Nome do usuário.', examples=['Lucas Azevedo']
    )
    credencial: str = Field(
        description='Alteração de credencial de uma conta.',
        examples=[True, False],
    )


class AdminPublic(UserPublic):
    is_admin: bool


class UserList(BaseModel):
    users: list[AdminPublic]


class Token(BaseModel):
    access_token: str
    token_type: str
