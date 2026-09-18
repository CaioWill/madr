from http import HTTPStatus
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database_conect import get_session
from madr.models import User
from madr.schemas.schema_Auths import Token
from madr.security import created_token, get_current, verificacao

router = APIRouter(prefix='/auth', tags=['auth'])

Session = Annotated[AsyncSession, Depends(get_session)]
UserT = Annotated[User, Depends(get_current)]

OAuth2form = Annotated[OAuth2PasswordRequestForm, Depends()]


# Endpoint para criação do token - Login
@router.post('/token', response_model=Token)
async def login_for_access_token(
    session: Session,
    # Um fomulario de login ja feito do FastAPI
    form_data: OAuth2form,
):
    # Buscando o email que veio do formulario no db
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )  # No formulario vem como username
    # Mas a gente oque vai usar

    # Conferindo se o email existe no db
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    # Conferindo se a hash da senha bate com o hash do banco
    if not verificacao(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    # Criando o Token jwt enviando o sub
    access_token = created_token({'sub': user.email})

    # Enviando o token criado
    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.post('/refresh_token', status_code=HTTPStatus.OK, response_model=Token)
def refresh_token(user: UserT):
    new_token = created_token(data={'sub': user.email})

    return {'access_token': new_token, 'token_type': 'Bearer'}
