"""initial schema

Revision ID: a6c5295ff241
Revises:
Create Date: 2025-08-05 14:48:08.640101
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a6c5295ff241'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('announcements',
        sa.Column('guid', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('announcement_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('application_deadline', sa.DateTime(timezone=True), nullable=False),
        sa.Column('eligible_institution', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('sectors', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('image_url', sa.String(), nullable=False),
        sa.Column('link', sa.String(), nullable=False),
        sa.Column('project_duration', sa.String(), nullable=False),
        sa.Column('budget_support', sa.String(), nullable=False),
        sa.Column('application_language', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('guid')
    )
    op.create_index(op.f('ix_announcements_guid'), 'announcements', ['guid'], unique=False)

    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.Enum('USER', 'ADMIN', name='role_enum'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('linkedin', sa.String(length=255), nullable=False),
        sa.Column('institution', sa.String(length=255), nullable=False),
        sa.Column('profession', sa.String(length=100), nullable=False),
        sa.Column('sectors', postgresql.ARRAY(sa.String()), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    op.create_table('passwords',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('last_changed', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    op.create_table('saved_announcements',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('announcement_guid', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['announcement_guid'], ['announcements.guid'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'announcement_guid')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('saved_announcements')
    op.drop_table('passwords')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_announcements_guid'), table_name='announcements')
    op.drop_table('announcements')