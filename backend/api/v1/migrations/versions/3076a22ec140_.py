"""empty message

Revision ID: 3076a22ec140
Revises: 2900e8c794e5
Create Date: 2015-11-27 12:01:26.913596

"""

# revision identifiers, used by Alembic.
revision = '3076a22ec140'
down_revision = '2900e8c794e5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('plan', sa.Column('plan_bought', sa.Date(), nullable=True))
    op.add_column('plan', sa.Column('plan_expires', sa.Date(), nullable=True))
    op.add_column('plan', sa.Column('plan_last_change', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('plan', 'plan_last_change')
    op.drop_column('plan', 'plan_expires')
    op.drop_column('plan', 'plan_bought')
    ### end Alembic commands ###