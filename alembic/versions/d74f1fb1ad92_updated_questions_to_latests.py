"""updated questions to latests

Revision ID: d74f1fb1ad92
Revises: 99b41fc771be
Create Date: 2023-06-26 23:36:06.308070

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd74f1fb1ad92'
down_revision = '99b41fc771be'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('questions', sa.Column('num_answer', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('questions', 'num_answer')
    # ### end Alembic commands ###
