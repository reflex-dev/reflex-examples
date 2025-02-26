"""empty message

Revision ID: 277cad49d2b0
Revises: 7aaec6b87d88
Create Date: 2024-05-30 10:58:18.235598

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "277cad49d2b0"
down_revision: Union[str, None] = "7aaec6b87d88"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("customer", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("date", sqlmodel.sql.sqltypes.AutoString(), nullable=False)
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("customer", schema=None) as batch_op:
        batch_op.drop_column("date")

    # ### end Alembic commands ###
