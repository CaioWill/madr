from dataclasses import asdict
from datetime import datetime
from http import HTTPStatus

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.models import User
from madr.security import verificacao


@pytest.mark.asyncio
async def test_criacao_de_usuario(client, session: AsyncSession):
    response = client.post(
        '/login/',
        json={
            'username': 'test',
            'email': 'test@test.com',
            'password': 'test',
        },
    )

    response2 = await session.scalar(
        select(User).where(User.username == response.json()['username'])
    )
    print(asdict(response2))
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'username': 'test', 'email': 'test@test.com'}


@pytest.mark.asyncio
async def test_criacao_de_usuario_time(create_user, session: AsyncSession):
    user = asdict(create_user)

    response = await session.scalar(
        select(User).where(User.username == user['username'])
    )

    response = asdict(response)
    response['password'] = verificacao(
        create_user.clean_password, response['password']
    )
    # print(user)

    assert response == {
        'id': 1,
        'username': 'test0',
        'email': 'test0@test.com',
        'password': True,
        'is_admin': False,
        'criacao': datetime(2026, 8, 21, 0, 0),
        'atualizacao': datetime(2026, 8, 21, 0, 0),
        'empretimos': [],
    }


def test_conflito_na_criacao_de_usuario_username(client, create_user):
    response = client.post(
        '/login/',
        json={
            'username': 'test0',
            'email': 'test@test.com',
            'password': 'test',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username já existente'}


def test_conflito_na_criacao_de_usuario_email(client, create_user):
    response = client.post(
        '/login/',
        json={
            'username': 'test10',
            'email': 'test0@test.com',
            'password': 'test',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email já existente'}


def test_atualizacao_de_conta(client, create_user, token):
    response = client.put(
        '/login/update_user',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'testest', 'password': 'testest'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'testest',
        'email': 'test0@test.com',
    }


def test_atualizacao_de_conta_conflito(
    client, create_user, outher_user, token
):
    response = client.put(
        '/login/update_user',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'test1', 'password': 'testest'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User name already exists'}


def test_deletar_usuario(client, create_user, token):
    response = client.delete(
        '/login/delete',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
