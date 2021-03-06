"""changed password type

Revision ID: d800626354e4
Revises: 74932c80411d
Create Date: 2022-02-02 18:37:16.499558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd800626354e4'
down_revision = '74932c80411d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'password',
               existing_type=sa.VARCHAR(length=72),
               type_=sa.Text(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'password',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=72),
               existing_nullable=False)
    # ### end Alembic commands ###
