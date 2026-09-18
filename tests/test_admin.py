from http import HTTPStatus

from madr.settings import Settings


def test_transformando_conta_em_admin(client, create_user, token):
    response = client.put(
        '/admin/',
        headers={'Authorization': f'Bearer {token}'},
        json={'key': Settings().ADMIN_KEY},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'test0',
        'email': 'test0@test.com',
        'is_admin': True,
    }


def test_transformando_conta_em_admin_key_incorreta(
    client, create_user, token
):
    response = client.put(
        '/admin/',
        headers={'Authorization': f'Bearer {token}'},
        json={'key': 'test'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Senha de autorização incorreta'}


def test_tornando_outros_usuarios_admin(
    user_admin, outher_user, client, token
):
    response = client.put(
        '/admin/credenciais',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'test1', 'credencial': 'admin'},
    )

    assert response.status_code == HTTPStatus.OK


def test_tentando_alterar_credencial_de_outra_conta_sem_Ser_admin(
    create_user, outher_user, client, token
):
    response = client.put(
        '/admin/credenciais',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'test1', 'credencial': 'admin'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_tentando_alterar_credencial_de_uma_conta_inexistente(
    user_admin, client, token
):
    response = client.put(
        '/admin/credenciais',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'test1', 'credencial': 'admin'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_tentando_alterar_credencial_com_um_valor_incorreto(
    user_admin, outher_user, client, token
):
    response = client.put(
        '/admin/credenciais',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'test1', 'credencial': 'test'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_listando_usuarios_da_aplicacao(
    user_admin, outher_user, client, token
):
    response = client.get(
        '/admin/listar_usuarios',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {'username': 'test0', 'email': 'test0@test.com', 'is_admin': True},
            {
                'username': 'test1',
                'email': 'test1@test.com',
                'is_admin': False,
            },
        ]
    }


def test_nao_autorizado_para_listar_usuarios_da_aplicacao(
    create_user, outher_user, client, token
):
    response = client.get(
        '/admin/listar_usuarios',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_deletando_contas_de_outros_usuarios(
    user_admin, outher_user, client, token
):
    response = client.delete(
        f'/admin/delete{outher_user.username}',
        headers={'Authorization': f'Bearer {token}'},
    )
    name = outher_user.username

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'mensagem': f'Conta com username: {name} deletada permanetimente!'
    }


def test_tentando_deletar_conta_de_usuarios_inexistente(
    user_admin, client, token
):
    name = 'testest'
    response = client.delete(
        f'/admin/delete{name}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Usuario: {name} Não encontrado'}
