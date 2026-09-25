from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from freezegun import freeze_time
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from madr.app import app
from madr.database_conect import get_session
from madr.models import User, tabelas
from madr.security import criptografar
from madr.settings import Settings
from tests.factorry import UserFactory

time = datetime(2026, 8, 21)


# fixture do cliente
@pytest.fixture
def client(session):

    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


# fixture da sessão
@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        yield create_async_engine(postgres.get_connection_url())

@pytest_asyncio.fixture
async def session(engine):

    async with engine.begin() as conn:
        await conn.run_sync(tabelas.metadata.create_all)


    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


    async with engine.begin() as conn:
        await conn.run_sync(tabelas.metadata.drop_all)


# gancho para alterar o time
@contextmanager
def _mock_db_time(*, model, time=time):

    # um gacho para fazer alterações
    # tem que ter os tres parametros mesmo sem usar para o event funcionar
    def fake_time_hook(mapper, connection, target):
        # (Connection) é a conexão
        # (Target) é o objeto

        # hasattr verifica se objeto que veio tem o atributo antes de replace
        if hasattr(target, 'criacao'):
            target.criacao = time

        if hasattr(target, 'atualizacao'):
            target.atualizacao = time

    # é tipo o trigger do postgre no python
    event.listen(model, 'before_insert', fake_time_hook)

    # Pausa a função e manda o time para a função que chamou
    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest_asyncio.fixture
async def create_user(session: AsyncSession):
    password = 'senha123'
    user = UserFactory(password=criptografar(password))

    with _mock_db_time(model=User):
        session.add(user)
        await session.commit()
        await session.refresh(user)

    # gambiarra, para conseguir a senha para fazer a verificação
    # não pessiste no banco
    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def outher_user(session: AsyncSession):
    user = UserFactory()
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@pytest.fixture
def token(client, create_user):
    response = client.post(
        '/auth/token',
        data={
            'username': create_user.email,
            'password': create_user.clean_password,
        },
    )

    return response.json()['access_token']


@pytest.fixture
def user_admin(create_user, client, token):
    user = client.put(
        '/admin/',
        headers={'Authorization': f'Bearer {token}'},
        json={'key': Settings().ADMIN_KEY},
    )

    return user


@pytest.fixture
def create_author(user_admin, token, client):
    autor = client.post(
        '/autores/',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'test'},
    )

    return autor


@pytest.fixture
def create_book(user_admin, token, create_author, client):
    livro = client.post(
        '/livros/adicionar_livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'testest',
            'author': 'test',
            'publication': '2026-08-22',
            'estoque': 1,
        },
    )
    return livro


@pytest.fixture
def creat_empretimo(user_admin, token, create_book, client):
    with freeze_time('2026-08-21'):
        empretimo = client.post(
            '/emprestimos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'livro': 'testest',
                'author': 'test',
                'data_entrega': '2026-08-22',
            },
        )

    return empretimo


@pytest.fixture(autouse=True)
def reset_user_factory_sequence():
    UserFactory.reset_sequence(force=True)
