from http import HTTPStatus


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
