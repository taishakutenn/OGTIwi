from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f4ed59993b4'
down_revision: Union[str, None] = 'aef68e4f738d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Изменяем тип столбцов с DateTime на Date
    op.alter_column('articles', 'created_date', type_=sa.Date())
    op.alter_column('articles', 'updated_date', type_=sa.Date())
    op.alter_column('users', 'created_date', type_=sa.Date())
    op.alter_column('requests', 'created_date', type_=sa.Date())
    op.alter_column('requests', 'reviewed_date', type_=sa.Date())


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем тип столбцов обратно на DateTime
    op.alter_column('articles', 'created_date', type_=sa.DateTime())
    op.alter_column('articles', 'updated_date', type_=sa.DateTime())
    op.alter_column('users', 'created_date', type_=sa.DateTime())
    op.alter_column('requests', 'created_date', type_=sa.DateTime())
    op.alter_column('requests', 'reviewed_date', type_=sa.DateTime())