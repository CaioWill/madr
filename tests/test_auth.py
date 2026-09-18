from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from freezegun import freeze_time
from jwt import encode

from madr.settings import Settings


def criar_token_fake(data, key: str = Settings().SECRET_KEY):
    payload = data

    expiracao = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update({'exp': expiracao})

    token = encode(payload, key, algorithm=Settings().ALGORITHM)

    return token


def test_email_senha_incorreto(create_user, client):
    response = client.post(
        '/auth/token', data={'username': create_user.email, 'password': '1234'}
    )

    response2 = client.post(
        '/auth/token',
        data={'username': 'string', 'password': create_user.clean_password},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}

    assert response2.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_tempo_excedido_do_token(create_user, client):

    with freeze_time('2026-09-19 14:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': create_user.email,
                'password': create_user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2026-09-19 14:31:00'):
        response = client.put(
            '/login/update_user',
            headers={'Authorization': f'Bearer {token}'},
            json={'username': 'testest', 'password': '#testest'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_sub_nao_eixitest_no_db(create_user, client):

    token = criar_token_fake({'sub': 'test'})

    response = client.put(
        '/login/update_user',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'testest', 'password': '#testest'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_sub_nao_foi_enviado(create_user, client):

    token = criar_token_fake({'xp': 'test'})

    response = client.put(
        '/login/update_user',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'testest', 'password': '#testest'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_token_criado_de_forma_errada(create_user, client):

    token = criar_token_fake({'sub': 'test'}, '123')

    response = client.put(
        '/login/update_user',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'testest', 'password': '#testest'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_refresh_token(create_user, client):

    with freeze_time('2026-09-19 14:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': create_user.email,
                'password': create_user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2026-09-19 14:29:00'):
        response = client.post(
            '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.OK


def test_tentando_fazer_refresh_com_tempo_excedido_do_token(
    client, create_user
):
    with freeze_time('2026-04-09 14:30:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': create_user.email,
                'password': create_user.clean_password,
            },
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2026-04-09 15:01:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Cloud not validate credentials'}
