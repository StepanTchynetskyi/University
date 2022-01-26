"""added student, teacher and position models

Revision ID: 4320b5a27aa0
Revises: 
Create Date: 2022-01-25 15:33:00.719681

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4320b5a27aa0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('position',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('position_name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('first_name', sa.String(length=60), nullable=False),
    sa.Column('last_name', sa.String(length=80), nullable=False),
    sa.Column('password', sa.LargeBinary(), nullable=False),
    sa.Column('age', sa.SmallInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('student',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('year_of_study', sa.SmallInteger(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('teacher',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('position_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['position_id'], ['position.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('students')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('students',
    sa.Column('id', postgresql.UUID(), autoincrement=False, nullable=False),
    sa.Column('year_of_study', sa.SMALLINT(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='students_pkey')
    )
    op.drop_table('teacher')
    op.drop_table('student')
    op.drop_table('user')
    op.drop_table('position')
    # ### end Alembic commands ###