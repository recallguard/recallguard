"""Add alerts table"""
from alembic import op
import sqlalchemy as sa
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('recall_id', sa.String(), nullable=False),
        sa.Column('channel', sa.String(), nullable=False),
        sa.Column('sent_at', sa.String()),
        sa.Column('read_at', sa.String()),
        sa.Column('error', sa.Text()),
    )

def downgrade() -> None:
    op.drop_table('alerts')
