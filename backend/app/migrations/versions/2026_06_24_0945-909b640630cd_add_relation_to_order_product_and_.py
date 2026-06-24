"""add relation to order_product and product

Revision ID: 909b640630cd
Revises: f0dffca5692e
Create Date: 2026-06-24 09:45:06.466070

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '909b640630cd'
down_revision: Union[str, Sequence[str], None] = 'f0dffca5692e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the mistyped table first so its `uq_order_product` constraint name
    # is freed before the corrected table reuses it.
    op.drop_table('orderproductss')
    op.create_table('orderproducts',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order_id', 'product_id', name='uq_order_product')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('orderproducts')
    op.create_table('orderproductss',
    sa.Column('order_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('price', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('quantity', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], name=op.f('orderproductss_order_id_fkey')),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name=op.f('orderproductss_product_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('orderproductss_pkey')),
    sa.UniqueConstraint('order_id', 'product_id', name=op.f('uq_order_product'), postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
