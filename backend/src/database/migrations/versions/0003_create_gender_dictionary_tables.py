"""Create gender_dictionary tables

Revision ID: 0003
Revises: 0002
Create Date: 2024-07-12 14:45:26.998556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gender_dictionary',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('femininum', sa.String(), nullable=False),
    sa.Column('masculinum', sa.String(), nullable=False),
    sa.Column('comment', sa.String(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gender_dictionary_suggestions',
    sa.Column('gender_dictionary_id', sa.BigInteger(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['gender_dictionary_id'], ['gender_dictionary.id'], ),
    sa.PrimaryKeyConstraint('gender_dictionary_id', 'type')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('gender_dictionary_suggestions')
    op.drop_table('gender_dictionary')
    # ### end Alembic commands ###
