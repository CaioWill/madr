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
Get_user = Annotated[User, Depends(get_current)]

OAuth2form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post(
    '/token',
    response_model=Token,
    summary='Criação de token de login.',
    response_description='Token criado com sucesso!',
)
async def login_for_access_token(
    session: Session,
    form_data: OAuth2form,
):
    """
    Endpoint para fazer a criação do token para login
    """

    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verificacao(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = created_token({'sub': user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.post(
    '/refresh_token',
    status_code=HTTPStatus.OK,
    response_model=Token,
    summary='Refresh do token do usuário.',
    response_description='Refresh realizado com sucesso!',
)
def refresh_token(user: Get_user):
    """
    Endpoint para fazer refresh de tokens de usuários.
    """
    new_token = created_token(data={'sub': user.email})

    return {'access_token': new_token, 'token_type': 'Bearer'}
