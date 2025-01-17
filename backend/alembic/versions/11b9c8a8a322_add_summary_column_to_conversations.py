"""Add summary column to conversations

Revision ID: 11b9c8a8a322
Revises: 
Create Date: 2025-01-13 09:30:30.856613

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision: str = '11b9c8a8a322'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns('conversations')]

    if 'summary' not in columns:
        op.add_column('conversations', sa.Column('summary', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('conversations', 'summary')
