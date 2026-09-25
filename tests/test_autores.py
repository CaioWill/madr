from http import HTTPStatus


def test_criancao_de_romancista(user_admin, client, token):
    response = client.post(
        '/autores/',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'test'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'mensagem': 'Author: test adicionado com sucesso!'
    }


def test_conflito_de_criancao_de_romancista(user_admin, client, token):
    client.post(
        '/autores/',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'test'},
    )

    response = client.post(
        '/autores/',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'test'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Author já cadastrado.'}


def test_listar_autores(create_user, token, client):
    response = client.get(
        '/autores/listar_authores',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'autores': []}


def test_listar_autores_com_autores_cadastrado(user_admin, token, client):
    client.post(
        '/autores/',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'test'},
    )

    response = client.get(
        '/autores/listar_authores',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'autores': [{'name': 'test'}]}


def test_deletar_romancista(user_admin, token, client):
    client.post(
        '/autores/',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'test'},
    )
    autor = 'test'

    response = client.delete(
        f'/autores/deletar_author{autor}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'mensagem': f'Author {autor} deletado!'}


def test_deletar_romancista_que_nao_existe(user_admin, token, client):

    autor = 'test'

    response = client.delete(
        f'/autores/deletar_author{autor}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Author {autor} não encontrado!'}
