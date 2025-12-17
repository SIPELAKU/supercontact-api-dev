"""add sequence

Revision ID: 3f6658ebac84
Revises: 184923007e13
Create Date: 2025-12-16 23:10:06.835127

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '3f6658ebac84'
down_revision: Union[str, Sequence[str], None] = '184923007e13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
