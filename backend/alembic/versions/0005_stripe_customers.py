"""add stripe customers"""
from alembic import op
import sqlalchemy as sa

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'stripe_customers',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), unique=True),
        sa.Column('stripe_customer_id', sa.String()),
        sa.Column('subscription_id', sa.String()),
        sa.Column('plan', sa.String(), server_default='free'),
        sa.Column('quota', sa.Integer(), server_default='100'),
        sa.Column('seats', sa.Integer(), server_default='1'),
    )


def downgrade() -> None:
    op.drop_table('stripe_customers')
