from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry

tabelas = registry()


@tabelas.mapped_as_dataclass
class User:
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    credenciais: Mapped[str] = mapped_column(init=False, server_default='User')
    criacao: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    atualizacao: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), server_onupdate=func.now()
    )
