from datetime import date, datetime

from sqlalchemy import ForeignKey, false, func, true
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

tabelas = registry()


@tabelas.mapped_as_dataclass
class User:
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=false(), nullable=False)
    criacao: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    atualizacao: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), server_onupdate=func.now()
    )
    empretimos: Mapped[list['Empretimos']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
        default_factory=list,
        back_populates='solicitador',
    )


@tabelas.mapped_as_dataclass
class Romancistas:
    __tablename__ = 'romancistas'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    update_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), server_onupdate=func.now()
    )
    livros: Mapped[list['Livros']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        default_factory=list,
        lazy='selectin',
        back_populates='author',
    )


@tabelas.mapped_as_dataclass
class Livros:
    __tablename__ = 'livros'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    publication: Mapped[date]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    update_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), server_onupdate=func.now()
    )
    author_id: Mapped[int] = mapped_column(ForeignKey(Romancistas.id))
    author: Mapped['Romancistas'] = relationship(
        init=False, lazy='selectin', back_populates='livros'
    )
    estoque: Mapped[int]


@tabelas.mapped_as_dataclass
class Empretimos:
    __tablename__ = 'emprestimos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    livros_id: Mapped[int] = mapped_column(
        ForeignKey(Livros.id, ondelete='CASCADE')
    )
    data_solicitacao: Mapped[date] = mapped_column(
        init=False, server_default=func.now()
    )
    data_entrega: Mapped[date]
    ativo: Mapped[bool] = mapped_column(default=true(), nullable=False)
    livro: Mapped['Livros'] = relationship(init=False, lazy='selectin')
    solicitador: Mapped['User'] = relationship(
        init=False, lazy='selectin', back_populates='empretimos'
    )
