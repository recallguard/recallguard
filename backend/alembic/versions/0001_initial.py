"""Initial tables"""

from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('created_at', sa.String(), nullable=False),
    )
    op.create_table(
        'products',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
    )
    op.create_table(
        'recalls',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('product', sa.String(), nullable=False),
        sa.Column('hazard', sa.Text()),
        sa.Column('recall_date', sa.String()),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('fetched_at', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'source'),
    )


def downgrade() -> None:
    op.drop_table('recalls')
    op.drop_table('products')
    op.drop_table('users')
