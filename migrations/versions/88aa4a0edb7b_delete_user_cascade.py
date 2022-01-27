"""delete user cascade

Revision ID: 88aa4a0edb7b
Revises: 92245fd38e55
Create Date: 2022-01-26 16:44:34.406850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88aa4a0edb7b'
down_revision = '92245fd38e55'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('student_id_fkey', 'student', type_='foreignkey')
    op.create_foreign_key(None, 'student', 'user', ['id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'student', type_='foreignkey')
    op.create_foreign_key('student_id_fkey', 'student', 'user', ['id'], ['id'])
    # ### end Alembic commands ###