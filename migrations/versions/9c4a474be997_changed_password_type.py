"""changed password type

Revision ID: 9c4a474be997
Revises: 4320b5a27aa0
Create Date: 2022-01-25 16:52:58.262722

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9c4a474be997'
down_revision = '4320b5a27aa0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'password',
               existing_type=postgresql.BYTEA(),
               type_=sa.String(length=72),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'password',
               existing_type=sa.String(length=72),
               type_=postgresql.BYTEA(),
               existing_nullable=False)
    # ### end Alembic commands ###
