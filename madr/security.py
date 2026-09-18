from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database_conect import get_session
from madr.models import User
from madr.settings import Settings

pwd_contexto = PasswordHash.recommended()

Session = Annotated[AsyncSession, Depends(get_session)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def criptografar(senha):
    return pwd_contexto.hash(senha)


def verificacao(senha: str, hash: str):
    return pwd_contexto.verify(senha, hash)


def created_token(data: dict):
    payload = data.copy()

    expiracao = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update({'exp': expiracao})

    token = encode(
        payload, Settings().SECRET_KEY, algorithm=Settings().ALGORITHM
    )

    return token


async def get_current(
    session: Session,
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Cloud not validate credentials',
        headers={'WWW-Autheticate': 'Bearer'},
    )

    try:
        playload = decode(
            token, Settings().SECRET_KEY, algorithms=Settings().ALGORITHM
        )

        subject_email = playload.get('sub')

        if not subject_email:
            raise credentials_exception

    except DecodeError:
        raise credentials_exception

    except ExpiredSignatureError:
        raise credentials_exception

    user = await session.scalar(
        select(User).where(User.email == subject_email)
    )

    if not user:
        raise credentials_exception

    return user


def get_current_admin(current_user: Annotated[User, Depends(get_current)]):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    return current_user
