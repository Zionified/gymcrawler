"""added variables in action and default values

Revision ID: 2ad9fa953ffc
Revises: ab8852b316bf
Create Date: 2023-06-28 01:56:15.175213

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2ad9fa953ffc'
down_revision = 'ab8852b316bf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('action', sa.Column('other_muscle_types', sa.Text(), nullable=False, comment='other muscles involved'))
    op.add_column('action', sa.Column('video', sa.String(length=1024), nullable=False, comment='video instruction'))
    op.drop_column('action', 'other_muscle_type')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('action', sa.Column('other_muscle_type', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=128), nullable=False, comment='other muscle involved'))
    op.drop_column('action', 'video')
    op.drop_column('action', 'other_muscle_types')
    # ### end Alembic commands ###
