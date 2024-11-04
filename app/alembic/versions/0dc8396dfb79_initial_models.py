"""initial models 

Revision ID: 0dc8396dfb79
Revises: 0c68957eb259
Create Date: 2024-11-04 10:45:20.880366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0dc8396dfb79'
down_revision: Union[str, None] = '0c68957eb259'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('url_id', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('disabled', sa.Boolean(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_by', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_created_by'), 'users', ['created_by'], unique=False)
    op.create_index(op.f('ix_users_url_id'), 'users', ['url_id'], unique=True)
    op.create_table('devices',
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('device_token', sa.String(), nullable=False),
    sa.Column('device_type', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_by', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('device_token')
    )
    op.create_index(op.f('ix_devices_created_by'), 'devices', ['created_by'], unique=False)
    op.create_table('notifications',
    sa.Column('notification_id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('device_id', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('body', sa.String(), nullable=False),
    sa.Column('image', sa.String(), nullable=True),
    sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('notification_status', sa.String(), nullable=False),
    sa.Column('notification_type', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_by', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_created_by'), 'notifications', ['created_by'], unique=False)
    op.create_index(op.f('ix_notifications_notification_id'), 'notifications', ['notification_id'], unique=True)
    op.drop_index('ix_todos_created_by', table_name='todos')
    op.drop_table('todos')
    op.drop_index('ix_auth_user_created_by', table_name='auth_user')
    op.drop_index('ix_auth_user_url_id', table_name='auth_user')
    op.drop_table('auth_user')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auth_user',
    sa.Column('url_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('full_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('hashed_password', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('disabled', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_by', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='auth_user_pkey')
    )
    op.create_index('ix_auth_user_url_id', 'auth_user', ['url_id'], unique=True)
    op.create_index('ix_auth_user_created_by', 'auth_user', ['created_by'], unique=False)
    op.create_table('todos',
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('is_chceked', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('created_by', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='todos_pkey')
    )
    op.create_index('ix_todos_created_by', 'todos', ['created_by'], unique=False)
    op.drop_index(op.f('ix_notifications_notification_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_created_by'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_devices_created_by'), table_name='devices')
    op.drop_table('devices')
    op.drop_index(op.f('ix_users_url_id'), table_name='users')
    op.drop_index(op.f('ix_users_created_by'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###