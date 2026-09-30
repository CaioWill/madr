from datetime import date
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database_conect import get_session
from madr.models import Empretimos, Livros, Romancistas, User
from madr.schemas.schema import Mensagem
from madr.schemas.schema_empretimos import (
    DevolverEmprestimo,
    Emprestimos_public,
    EmprestimosSchema,
    ListEmprestimos,
)
from madr.security import format_name, get_current, get_current_admin

router = APIRouter(prefix='/emprestimos', tags=['emprestimos'])

Session = Annotated[AsyncSession, Depends(get_session)]
Admin = Annotated[User, Depends(get_current_admin)]
UserT = Annotated[User, Depends(get_current)]


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=Emprestimos_public
)
async def solicitacao_emprestimo(
    emprestimo: EmprestimosSchema, user: UserT, session: Session
):
    emprestimo.livro = format_name(emprestimo.livro)
    emprestimo.author = format_name(emprestimo.author)

    if emprestimo.data_entrega <= date.today():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Digite uma data de entrega válida!',
        )

    author = await session.scalar(
        select(Romancistas).where(Romancistas.name == emprestimo.author)
    )

    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Author: {emprestimo.author} não encontrado!',
        )

    livro = await session.scalar(
        select(Livros).where(
            Livros.name == emprestimo.livro, Livros.author_id == author.id
        )
    )

    if not livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Livro: {emprestimo.livro} não encontrado!',
        )

    if livro.estoque < 1:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'Livro: {emprestimo.livro} sem estoque!',
        )

    new_emprestimo = Empretimos(
        user_id=user.id,
        livros_id=livro.id,
        data_entrega=emprestimo.data_entrega,
    )

    livro.estoque -= 1

    session.add(new_emprestimo)
    session.add(livro)
    await session.commit()
    await session.refresh(new_emprestimo)

    response = Emprestimos_public(
        solicitador=user.username,
        livro=emprestimo.livro,
        author=emprestimo.author,
        data_entrega=emprestimo.data_entrega,
        ativo=new_emprestimo.ativo,
    )

    return response


@router.get(
    '/listar_emprestimos',
    response_model=ListEmprestimos,
    status_code=HTTPStatus.OK,
)
async def listar_emprestimos(user: Admin, session: Session):
    lista_empretimos = []

    lista = await session.scalars(select(Empretimos))
    for emprestimos in lista:
        lista_empretimos.append({
            'livro': emprestimos.livro.name,
            'author': emprestimos.livro.author.name,
            'solicitador': emprestimos.solicitador.username,
            'data_entrega': emprestimos.data_entrega,
            'ativo': emprestimos.ativo,
        })
    return {'emprestimos': lista_empretimos}


@router.get(
    '/empretimos_ativos',
    status_code=HTTPStatus.OK,
    response_model=ListEmprestimos,
)
async def empretimos_ativos(user: UserT, session: Session):
    lista_emprestimos = []
    lista = await session.scalars(
        select(Empretimos).where(
            Empretimos.user_id == user.id, Empretimos.ativo
        )
    )

    for emprestimos in lista:
        lista_emprestimos.append({
            'livro': emprestimos.livro.name,
            'author': emprestimos.livro.author.name,
            'solicitador': emprestimos.solicitador.username,
            'data_entrega': emprestimos.data_entrega,
            'ativo': emprestimos.ativo,
        })

    return {'emprestimos': lista_emprestimos}


@router.put(
    '/devolucao_emprestimo', status_code=HTTPStatus.OK, response_model=Mensagem
)
async def devolucao_emprestimo(
    livro: DevolverEmprestimo, user: UserT, session: Session
):

    livro.nome_livro = format_name(livro.nome_livro)
    livro.nome_author = format_name(livro.nome_author)

    author = await session.scalar(
        select(Romancistas).where(Romancistas.name == livro.nome_author)
    )

    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Author: {livro.nome_author} não encontrado!',
        )

    livro_emprestado = await session.scalar(
        select(Livros).where(
            Livros.name == livro.nome_livro, Livros.author_id == author.id
        )
    )

    if not livro_emprestado:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Livro: {livro.nome_livro} não encontrado!',
        )

    emprestimo = await session.scalar(
        select(Empretimos).where(
            Empretimos.user_id == user.id,
            Empretimos.ativo,
            Empretimos.livros_id == livro_emprestado.id,
        )
    )

    if not emprestimo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Você não pegou o livro: {livro.nome_livro} emprestado.',
        )

    emprestimo.ativo = False

    livro_emprestado.estoque += 1

    session.add(emprestimo)
    await session.commit()
    await session.refresh(emprestimo)

    return {
        'mensagem': f'Livro {livro_emprestado.name} devolvido com sucesso.'
    }
