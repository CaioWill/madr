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
    create_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    update_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), server_onupdate=func.now()
    )
    loans: Mapped[list['Loans']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
        default_factory=list,
        back_populates='to_request',
    )


@tabelas.mapped_as_dataclass
class Authors:
    __tablename__ = 'Authors'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    update_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), server_onupdate=func.now()
    )
    books: Mapped[list['Books']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        default_factory=list,
        lazy='selectin',
        back_populates='author',
    )


@tabelas.mapped_as_dataclass
class Books:
    __tablename__ = 'Books'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    publication: Mapped[date]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    update_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), server_onupdate=func.now()
    )
    author_id: Mapped[int] = mapped_column(ForeignKey(Authors.id))
    author: Mapped['Authors'] = relationship(
        init=False, lazy='selectin', back_populates='books'
    )
    stock: Mapped[int]


@tabelas.mapped_as_dataclass
class Loans:
    __tablename__ = 'Loans'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    books_id: Mapped[int] = mapped_column(
        ForeignKey(Books.id, ondelete='CASCADE')
    )
    date_request: Mapped[date] = mapped_column(
        init=False, server_default=func.now()
    )
    date_deliver: Mapped[date]
    active: Mapped[bool] = mapped_column(default=true(), nullable=False)
    book: Mapped['Books'] = relationship(init=False, lazy='selectin')
    to_request: Mapped['User'] = relationship(
        init=False, lazy='selectin', back_populates='loans'
    )
