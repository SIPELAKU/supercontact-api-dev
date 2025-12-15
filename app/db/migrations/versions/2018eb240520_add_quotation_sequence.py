"""add quotation sequence

Revision ID: 2018eb240520
Revises: 6752e4ac9db9
Create Date: 2025-12-15 22:22:21.885269

"""
from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2018eb240520'
down_revision: Union[str, Sequence[str], None] = '6752e4ac9db9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    year = datetime.now(timezone.utc).strftime("%y")
    op.execute(
        f"CREATE SEQUENCE IF NOT EXISTS quotation_{year}_seq START 1;"
    )


def downgrade() -> None:
    """Downgrade schema."""
    year = datetime.now(timezone.utc).strftime("%y")
    op.execute(
        f"DROP SEQUENCE IF EXISTS quotation_{year}_seq;"
    )
