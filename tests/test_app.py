from http import HTTPStatus


def test_app_tela_inicial(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
