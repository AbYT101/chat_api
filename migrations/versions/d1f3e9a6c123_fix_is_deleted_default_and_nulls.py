"""fix is_deleted default and existing NULLs

Revision ID: d1f3e9a6c123
Revises: b671ca25473b
Create Date: 2026-01-13 19:XX:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d1f3e9a6c123"
down_revision: Union[str, Sequence[str], None] = "b671ca25473b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Set existing NULLs to False
    op.execute("UPDATE messages SET is_deleted = false WHERE is_deleted IS NULL")
    # Set server default and make column non-nullable
    op.alter_column(
        "messages",
        "is_deleted",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text("false"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Revert to nullable and remove server default
    op.alter_column(
        "messages",
        "is_deleted",
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=None,
    )
    # Note: we do not revert existing rows to NULL to avoid data loss
