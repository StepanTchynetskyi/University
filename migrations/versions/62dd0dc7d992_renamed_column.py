"""renamed column

Revision ID: 62dd0dc7d992
Revises: 5d3d09d8948c
Create Date: 2022-01-28 19:32:17.827871

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62dd0dc7d992'
down_revision = '5d3d09d8948c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('specialty', sa.Column('specialty_year', sa.Date(), nullable=False))
    op.drop_column('specialty', 'year')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('specialty', sa.Column('year', sa.DATE(), autoincrement=False, nullable=False))
    op.drop_column('specialty', 'specialty_year')
    # ### end Alembic commands ###
