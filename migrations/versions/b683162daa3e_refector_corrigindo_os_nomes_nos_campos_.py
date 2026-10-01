"""refector: Corrigindo os nomes nos campos para o padrão ingles.

Revision ID: b683162daa3e
Revises: 3d83cca4f19a
Create Date: 2026-10-01 11:03:06.822616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b683162daa3e'
down_revision: Union[str, Sequence[str], None] = '3d83cca4f19a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # tabelas (as FKs acompanham o rename sozinhas)
    op.rename_table('romancistas', 'Authors')
    op.rename_table('livros', 'Books')
    op.rename_table('emprestimos', 'Loans')

    # Books
    op.alter_column('Books', 'estoque', new_column_name='stock')

    # Loans
    op.alter_column('Loans', 'livros_id', new_column_name='books_id')
    op.alter_column('Loans', 'data_solicitacao', new_column_name='date_request')
    op.alter_column('Loans', 'data_entrega', new_column_name='date_deliver')
    op.alter_column('Loans', 'ativo', new_column_name='active')

    # Users
    op.alter_column('Users', 'criacao', new_column_name='create_at')
    op.alter_column('Users', 'atualizacao', new_column_name='update_at')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('Users', 'update_at', new_column_name='atualizacao')
    op.alter_column('Users', 'create_at', new_column_name='criacao')

    op.alter_column('Loans', 'active', new_column_name='ativo')
    op.alter_column('Loans', 'date_deliver', new_column_name='data_entrega')
    op.alter_column('Loans', 'date_request', new_column_name='data_solicitacao')
    op.alter_column('Loans', 'books_id', new_column_name='livros_id')

    op.alter_column('Books', 'stock', new_column_name='estoque')

    op.rename_table('Loans', 'emprestimos')
    op.rename_table('Books', 'livros')
    op.rename_table('Authors', 'romancistas')