from http import HTTPStatus

import pytest
from freezegun import freeze_time
from sqlalchemy import select

from madr.models import Books


def test_criando_um_emprestimo(
    user_admin, token, create_book, client, creat_empretimo
):

    assert creat_empretimo.status_code == HTTPStatus.CREATED
    assert creat_empretimo.json() == {
        'book': 'testest',
        'author': 'test',
        'date_deliver': '2026-08-22',
        'to_request': 'test0',
        'active': True,
    }


def test_criando_um_emprestimo_data_de_entrega_errada(
    user_admin, token, create_book, client
):
    with freeze_time('2026-08-21'):
        response01 = client.post(
            '/loans/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'book': 'testest',
                'author': 'test',
                'date_deliver': '2026-08-20',
            },
        )
        response02 = client.post(
            '/loans/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'book': 'testest',
                'author': 'test',
                'date_deliver': '2026-08-21',
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
            '/loans/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'book': 'testest',
                'author': autor,
                'date_deliver': '2026-08-22',
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
            '/loans/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'book': livro,
                'author': 'test',
                'date_deliver': '2026-08-22',
            },
        )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Livro: {livro} não encontrado!'}


def test_criando_um_emprestimo_livro_sem_estoque(
    user_admin, token, create_author, client
):
    livro = 'oioi'
    client.post(
        '/books/create_book',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': livro,
            'author': 'test',
            'publication': '2026-08-22',
            'stock': 0,
        },
    )

    with freeze_time('2026-08-21'):
        response = client.post(
            '/loans/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'book': livro,
                'author': 'test',
                'date_deliver': '2026-08-22',
            },
        )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': f'Livro: {livro} sem estoque!'}


def test_listar_todos_emprestimos(user_admin, token, client):
    response = client.get(
        '/loans/list_loans',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'loans': []}


def test_listar_todos_emprestimos_com_emprestimo(
    user_admin, create_book, token, client, creat_empretimo
):

    response = client.get(
        '/loans/list_loans',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'loans': [
            {
                'to_request': 'test0',
                'book': 'testest',
                'author': 'test',
                'date_deliver': '2026-08-22',
                'active': True,
            }
        ]
    }


def test_listar_emprestimos_ativos_user(
    user_admin, create_book, token, client, creat_empretimo
):

    response = client.get(
        '/loans/loans_active',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'loans': [
            {
                'to_request': 'test0',
                'book': 'testest',
                'author': 'test',
                'date_deliver': '2026-08-22',
                'active': True,
            }
        ]
    }


def test_listar_emprestimos_ativos_sem_ter_ativos(
    user_admin, create_book, token, client, creat_empretimo
):

    test = client.put(
        '/loans/return_loans',
        headers={'Authorization': f'Bearer {token}'},
        json={'name_book': 'testest', 'name_author': 'test'},
    )

    response = client.get(
        '/loans/loans_active',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert test.status_code == HTTPStatus.OK
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'loans': []}


@pytest.mark.asyncio
async def test_devolver_livro(
    user_admin, creat_empretimo, token, client, session
):

    book = await session.scalar(select(Books).where(Books.id == 1))

    assert book.stock == 0

    response = client.put(
        '/loans/return_loans',
        headers={'Authorization': f'Bearer {token}'},
        json={'name_book': 'testest', 'name_author': 'test'},
    )

    book = await session.scalar(select(Books).where(Books.id == 1))

    assert book.stock == 1

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'mensagem': 'Livro testest devolvido com sucesso.'
    }


def test_devolver_livro_nome_author_errado(
    user_admin, creat_empretimo, token, client, session
):

    response = client.put(
        '/loans/return_loans',
        headers={'Authorization': f'Bearer {token}'},
        json={'name_book': 'testest', 'name_author': 'oioi'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author: oioi não encontrado!'}


def test_devolver_livro_nome_livro_errado(
    user_admin, creat_empretimo, token, client, session
):

    response = client.put(
        '/loans/return_loans',
        headers={'Authorization': f'Bearer {token}'},
        json={'name_book': 'oioi', 'name_author': 'test'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Livro: oioi não encontrado!'}


def test_devolver_livro_sem_ter_pego_ele(
    user_admin, create_book, token, client, session
):

    response = client.put(
        '/loans/return_loans',
        headers={'Authorization': f'Bearer {token}'},
        json={'name_book': 'testest', 'name_author': 'test'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': 'Você não pegou o livro: testest emprestado.'
    }
