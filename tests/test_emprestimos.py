from http import HTTPStatus

import pytest
from freezegun import freeze_time
from sqlalchemy import select

from madr.models import Livros


def test_criando_um_emprestimo(
    user_admin, token, create_book, client, creat_empretimo
):

    assert creat_empretimo.status_code == HTTPStatus.CREATED
    assert creat_empretimo.json() == {
        'solicitador': 'test0',
        'livro': 'testest',
        'author': 'test',
        'data_entrega': '2026-08-22',
        'ativo': True,
    }


def test_criando_um_emprestimo_data_de_entrega_errada(
    user_admin, token, create_book, client
):
    with freeze_time('2026-08-21'):
        response01 = client.post(
            '/emprestimos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'livro': 'testest',
                'author': 'test',
                'data_entrega': '2026-08-20',
            },
        )
        response02 = client.post(
            '/emprestimos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'livro': 'testest',
                'author': 'test',
                'data_entrega': '2026-08-21',
            },
        )

    assert response01.status_code == HTTPStatus.BAD_REQUEST
    assert response01.json() == {
        'detail': 'Digite uma data de entrega válida!'
    }

    assert response02.status_code == HTTPStatus.BAD_REQUEST
    assert response02.json() == {
        'detail': 'Digite uma data de entrega válida!'
    }


def test_criando_um_emprestimo_nome_author_errado(
    user_admin, token, create_book, client
):
    with freeze_time('2026-08-21'):
        autor = 'oioi'
        response = client.post(
            '/emprestimos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'livro': 'testest',
                'author': autor,
                'data_entrega': '2026-08-22',
            },
        )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Author: {autor} não encontrado!'}


def test_criando_um_emprestimo_nome_livro_errado(
    user_admin, token, create_book, client
):
    with freeze_time('2026-08-21'):
        livro = 'oioi'
        response = client.post(
            '/emprestimos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'livro': livro,
                'author': 'test',
                'data_entrega': '2026-08-22',
            },
        )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Livro: {livro} não encontrado!'}


def test_criando_um_emprestimo_livro_sem_estoque(
    user_admin, token, create_author, client
):
    livro = 'oioi'
    client.post(
        '/livros/adicionar_livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': livro,
            'author': 'test',
            'publication': '2026-08-22',
            'estoque': 0,
        },
    )

    with freeze_time('2026-08-21'):
        response = client.post(
            '/emprestimos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'livro': livro,
                'author': 'test',
                'data_entrega': '2026-08-22',
            },
        )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': f'Livro: {livro} sem estoque!'}


def test_listar_todos_emprestimos(user_admin, token, client):
    response = client.get(
        '/emprestimos/listar_emprestimos',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'emprestimos': []}


def test_listar_todos_emprestimos_com_emprestimo(
    user_admin, create_book, token, client, creat_empretimo
):

    response = client.get(
        '/emprestimos/listar_emprestimos',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'emprestimos': [
            {
                'solicitador': 'test0',
                'livro': 'testest',
                'author': 'test',
                'data_entrega': '2026-08-22',
                'ativo': True,
            }
        ]
    }


def test_listar_emprestimos_ativos_user(
    user_admin, create_book, token, client, creat_empretimo
):

    response = client.get(
        '/emprestimos/empretimos_ativos',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'emprestimos': [
            {
                'solicitador': 'test0',
                'livro': 'testest',
                'author': 'test',
                'data_entrega': '2026-08-22',
                'ativo': True,
            }
        ]
    }


def test_listar_emprestimos_ativos_sem_ter_ativos(
    user_admin, create_book, token, client, creat_empretimo
):

    client.put(
        '/emprestimos/devolucao_emprestimo',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome_livro': 'testest', 'nome_author': 'test'},
    )

    response = client.get(
        '/emprestimos/empretimos_ativos',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'emprestimos': []}


@pytest.mark.asyncio
async def test_devolver_livro(
    user_admin, creat_empretimo, token, client, session
):

    livro = await session.scalar(select(Livros).where(Livros.id == 1))

    assert livro.estoque == 0

    response = client.put(
        '/emprestimos/devolucao_emprestimo',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome_livro': 'testest', 'nome_author': 'test'},
    )

    livro = await session.scalar(select(Livros).where(Livros.id == 1))

    assert livro.estoque == 1

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'mensagem': 'Livro testest devolvido com sucesso.'
    }


def test_devolver_livro_nome_author_errado(
    user_admin, creat_empretimo, token, client, session
):

    response = client.put(
        '/emprestimos/devolucao_emprestimo',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome_livro': 'testest', 'nome_author': 'oioi'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author: oioi não encontrado!'}


def test_devolver_livro_nome_livro_errado(
    user_admin, creat_empretimo, token, client, session
):

    response = client.put(
        '/emprestimos/devolucao_emprestimo',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome_livro': 'oioi', 'nome_author': 'test'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Livro: oioi não encontrado!'}


def test_devolver_livro_sem_ter_pego_ele(
    user_admin, create_book, token, client, session
):

    response = client.put(
        '/emprestimos/devolucao_emprestimo',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome_livro': 'testest', 'nome_author': 'test'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': 'Você não pegou o livro: testest emprestado.'
    }
