from http import HTTPStatus


def test_app_tela_inicial(cliente):
    response = cliente.get('/')

    assert response.status_code == HTTPStatus.OK
