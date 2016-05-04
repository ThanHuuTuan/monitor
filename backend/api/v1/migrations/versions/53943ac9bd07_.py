"""empty message

Revision ID: 53943ac9bd07
Revises: 10bdab42fdfd
Create Date: 2015-11-23 15:00:55.741882

"""

# revision identifiers, used by Alembic.
revision = '53943ac9bd07'
down_revision = '10bdab42fdfd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('auth_user', sa.Column('plan_details', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'auth_user', 'plan', ['plan_details'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'auth_user', type_='foreignkey')
    op.drop_column('auth_user', 'plan_details')
    ### end Alembic commands ###