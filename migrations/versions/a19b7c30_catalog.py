"""Add the Star Wars catalog and per-user favorites.

Revision ID: a19b7c30
Revises: 0763d677d453
"""
from alembic import op
import sqlalchemy as sa
revision = "a19b7c30"
down_revision = "0763d677d453"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user") as batch:
        batch.alter_column("password", existing_type=sa.String(), type_=sa.String(255))
    op.create_table("planet", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("swapi_id", sa.String(20), unique=True), sa.Column("properties", sa.JSON()),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("climate", sa.String(100)), sa.Column("terrain", sa.String(100)), sa.Column("population", sa.String(30)))
    op.create_table("character", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("swapi_id", sa.String(20), unique=True), sa.Column("properties", sa.JSON()),
        sa.Column("name", sa.String(100), nullable=False), sa.Column("gender", sa.String(30)),
        sa.Column("height", sa.String(30)), sa.Column("mass", sa.String(30)), sa.Column("birth_year", sa.String(30)),
        sa.Column("planet_id", sa.Integer(), sa.ForeignKey("planet.id")))
    op.create_table("vehicle", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("swapi_id", sa.String(20), unique=True), sa.Column("properties", sa.JSON()),
        sa.Column("name", sa.String(100), nullable=False), sa.Column("model", sa.String(200)),
        sa.Column("manufacturer", sa.String(255)), sa.Column("passengers", sa.String(30)))
    for table, field, resource in [("favorite_planet", "planet_id", "planet"),
                                   ("favorite_character", "character_id", "character"),
                                   ("favorite_vehicle", "vehicle_id", "vehicle")]:
        op.create_table(table, sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), primary_key=True),
                        sa.Column(field, sa.Integer(), sa.ForeignKey(f"{resource}.id"), primary_key=True))


def downgrade():
    for table in ["favorite_vehicle", "favorite_character", "favorite_planet", "vehicle", "character", "planet"]:
        op.drop_table(table)
    with op.batch_alter_table("user") as batch:
        batch.alter_column("password", existing_type=sa.String(255), type_=sa.String())
