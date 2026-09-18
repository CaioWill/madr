from datetime import datetime

from sqlalchemy import ForeignKey, false, func
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
        init=False, cascade='all, delete-orphan', lazy='selectin'
    )


@tabelas.mapped_as_dataclass
class Livros:
    __tablename__ = 'livros'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    create: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    update_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), server_onupdate=func.now()
    )
    author: Mapped[int] = mapped_column(ForeignKey(Romancistas.id))
