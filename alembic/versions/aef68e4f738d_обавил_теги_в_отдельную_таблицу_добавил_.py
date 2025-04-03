"""обавил теги в отдельную таблицу, добавил таблицу для объеденения тегов и статей

Revision ID: aef68e4f738d
Revises: 
Create Date: 2025-03-24 09:31:01.369182

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aef68e4f738d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_articles_views', table_name='articles')
    op.drop_table('articles')
    op.drop_table('requests')
    op.drop_table('notifications')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('surname', sa.VARCHAR(), nullable=True),
    sa.Column('username', sa.VARCHAR(), nullable=True),
    sa.Column('about', sa.VARCHAR(), nullable=True),
    sa.Column('binary_avatar', sa.VARCHAR(), nullable=True),
    sa.Column('email', sa.VARCHAR(), nullable=True),
    sa.Column('hashed_password', sa.VARCHAR(), nullable=True),
    sa.Column('role', sa.VARCHAR(), nullable=True),
    sa.Column('created_date', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=1)
    op.create_index('ix_users_email', 'users', ['email'], unique=1)
    op.create_table('notifications',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('message', sa.VARCHAR(), nullable=False),
    sa.Column('is_read', sa.BOOLEAN(), nullable=True),
    sa.Column('created_date', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('requests',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('status', sa.VARCHAR(), nullable=True),
    sa.Column('created_date', sa.DATETIME(), nullable=True),
    sa.Column('reviewed_by', sa.INTEGER(), nullable=True),
    sa.Column('reviewed_date', sa.DATETIME(), nullable=True),
    sa.Column('comment', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('articles',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(), nullable=False),
    sa.Column('preview', sa.VARCHAR(), nullable=True),
    sa.Column('author_id', sa.INTEGER(), nullable=False),
    sa.Column('created_date', sa.DATETIME(), nullable=True),
    sa.Column('updated_date', sa.DATETIME(), nullable=True),
    sa.Column('article_text', sa.VARCHAR(), nullable=False),
    sa.Column('tags', sa.VARCHAR(), nullable=True),
    sa.Column('views', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_articles_views', 'articles', ['views'], unique=False)
    # ### end Alembic commands ###
