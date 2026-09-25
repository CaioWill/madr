from http import HTTPStatus

import pytest
from sqlalchemy import select

from madr.models import Livros


def test_criar_livro(user_admin, token, create_author, client):
    response = client.post(
        '/livros/adicionar_livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'testest',
            'author': 'test',
            'publication': '2026-08-22',
            'estoque': 1,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'name': 'testest',
        'publication': '2026-08-22',
        'author_id': 1,
        'estoque': 1,
    }


def test_criar_livro_estoque_menor_que_0(
    user_admin, token, create_author, client
):
    response = client.post(
        '/livros/adicionar_livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'testest',
            'author': 'test',
            'publication': '2026-08-22',
            'estoque': -1,
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Digite um valor de estoque valido'}


def test_criar_livro_sem_author(user_admin, token, client):
    response = client.post(
        '/livros/adicionar_livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'testest',
            'author': 'test',
            'publication': '2026-08-22',
            'estoque': 1,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author não encontrado!'}


def test_criar_livro_ja_existente(user_admin, token, create_author, client):
    client.post(
        '/livros/adicionar_livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'testest',
            'author': 'test',
            'publication': '2026-08-22',
            'estoque': 1,
        },
    )

    response = client.post(
        '/livros/adicionar_livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'testest',
            'author': 'test',
            'publication': '2026-08-22',
            'estoque': 1,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Livro já cadastrado no author!'}


def test_listar_livros(create_user, create_author, token, client):
    response = client.get(
        '/livros/list_livros', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'livros': []}


def test_listar_livros_author(user_admin, token, create_author, client):
    author = 'test'

    client.post(
        '/livros/adicionar_livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'testest',
            'author': author,
            'publication': '2026-08-22',
            'estoque': 1,
        },
    )

    response = client.get(
        f'/livros/list_livros_{author}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'livros': [
            {
                'name': 'testest',
                'publication': '2026-08-22',
                'author_id': 1,
                'estoque': 1,
            }
        ]
    }


def test_listar_livros_author_nao_existente(
    user_admin, token, create_author, client
):
    author = 'brandon'

    client.post(
        '/livros/adicionar_livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'testest',
            'author': 'test',
            'publication': '2026-08-22',
            'estoque': 1,
        },
    )

    response = client.get(
        f'/livros/list_livros_{author}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author não encontrado!'}


@pytest.mark.asyncio
async def test_atualizar_estoque(
    user_admin, token, create_book, client, session
):

    livro = await session.scalar(select(Livros).where(Livros.id == 1))

    assert livro.estoque == 1

    response = client.put(
        '/livros/atualizar_estoque',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'testest', 'author': 'test', 'new_inventory': 2},
    )

    test = 3

    assert response.status_code == HTTPStatus.OK
    assert response.json()['estoque'] == test


def test_atualizar_estoque_nome_livro_errado(
    user_admin, token, create_book, client
):
    response = client.put(
        '/livros/atualizar_estoque',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'oioi', 'author': 'test', 'new_inventory': 2},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Livro: oioi não encontrado!'}


def test_atualizar_estoque_nome_autor_errado(
    user_admin, token, create_book, client
):
    response = client.put(
        '/livros/atualizar_estoque',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'testest', 'author': 'oioi', 'new_inventory': 2},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Autor: oioi não encontrado!'}


def test_atualizar_estoque_valor_estoque_menor_que_zero(
    user_admin, token, create_book, client
):
    response = client.put(
        '/livros/atualizar_estoque',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'testest', 'author': 'test', 'new_inventory': -2},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': 'Livros não podem ter um estoque a baixo de zero'
    }


def test_deletar_livros(user_admin, token, create_author, client):
    livro = 'testest'
    client.post(
        '/livros/adicionar_livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': livro,
            'author': 'test',
            'publication': '2026-08-22',
            'estoque': 1,
        },
    )

    response = client.delete(
        f'/livros/deletar_livro?author=test&livro={livro}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'mensagem': f'Livro {livro} do author test deletado'
    }


def test_deletar_livros_que_nao_existe(
    user_admin, token, create_author, client
):
    client.post(
        '/livros/adicionar_livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'testest',
            'author': 'test',
            'publication': '2026-08-22',
            'estoque': 1,
        },
    )

    livro = 'oioi'

    response = client.delete(
        f'/livros/deletar_livro?author=test&livro={livro}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Livro: {livro} não encontrado!'}


def test_deletar_livros_nome_do_autor_errado(
    user_admin, token, create_author, client
):
    livro = 'testest'
    autor = 'oioi'

    client.post(
        '/livros/adicionar_livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': livro,
            'author': 'test',
            'publication': '2026-08-22',
            'estoque': 1,
        },
    )

    response = client.delete(
        f'/livros/deletar_livro?author={autor}&livro={livro}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Autor: oioi não encontrado!'}
