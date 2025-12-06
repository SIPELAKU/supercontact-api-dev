"""update role enum

Revision ID: c7e772ec5dda
Revises: 995eb60d9223
Create Date: 2025-12-04 23:54:01.403433

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7e772ec5dda"
down_revision: Union[str, Sequence[str], None] = "995eb60d9223"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
