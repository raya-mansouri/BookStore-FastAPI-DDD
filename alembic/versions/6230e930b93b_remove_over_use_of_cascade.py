"""remove over use of cascade

Revision ID: 6230e930b93b
Revises: cb4e652a7da9
Create Date: 2025-02-12 11:24:28.418032

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6230e930b93b'
down_revision: Union[str, None] = 'cb4e652a7da9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
