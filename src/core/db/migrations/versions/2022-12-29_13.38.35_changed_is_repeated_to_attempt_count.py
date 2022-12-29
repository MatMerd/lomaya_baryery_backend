"""changed is_repeated to attempt_count

Revision ID: de1d50a2cfbf
Revises: 0243cc563a4c
Create Date: 2022-12-29 13:38:35.147603

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'de1d50a2cfbf'
down_revision = '0243cc563a4c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reports', sa.Column('attempt_number', sa.Integer(), server_default='0', nullable=False))
    op.drop_column('reports', 'is_repeated')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reports', sa.Column('is_repeated', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('reports', 'attempt_number')
    # ### end Alembic commands ###
