"""empty message

Revision ID: 10bdab42fdfd
Revises: 306a458d9dcc
Create Date: 2015-11-23 14:41:59.449346

"""

# revision identifiers, used by Alembic.
revision = '10bdab42fdfd'
down_revision = '306a458d9dcc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('plan',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('plan_level', sa.String(length=20), nullable=True),
    sa.Column('plan_period', sa.String(length=20), nullable=True),
    sa.Column('plan_bought', sa.DateTime(), nullable=True),
    sa.Column('plan_expires', sa.DateTime(), nullable=True),
    sa.Column('plan_last_change', sa.DateTime(), nullable=True),
    sa.Column('plan_price', sa.String(length=10), nullable=True),
    sa.Column('plan_trial', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('plan')
    ### end Alembic commands ###
