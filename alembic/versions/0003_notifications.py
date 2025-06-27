"""Add subscriptions and sent_notifications"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('email_opt_in', sa.Integer(), nullable=False, server_default='0'))

    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recall_source', sa.String(), nullable=False),
        sa.Column('product_query', sa.String(), nullable=False),
        sa.Column('created_at', sa.String(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'sent_notifications',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('recall_id', sa.String(), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table('sent_notifications')
    op.drop_table('subscriptions')
    op.drop_column('users', 'email_opt_in')
