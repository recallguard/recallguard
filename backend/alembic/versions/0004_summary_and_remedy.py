"""Add recall summary and remedy updates"""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('recalls', sa.Column('summary_text', sa.Text(), nullable=True))
    op.add_column('recalls', sa.Column('next_steps', sa.Text(), nullable=True))
    op.add_column(
        'recalls',
        sa.Column('remedy_updates', sa.JSON(), server_default='[]', nullable=True),
    )


def downgrade() -> None:
    op.drop_column('recalls', 'remedy_updates')
    op.drop_column('recalls', 'next_steps')
    op.drop_column('recalls', 'summary_text')
