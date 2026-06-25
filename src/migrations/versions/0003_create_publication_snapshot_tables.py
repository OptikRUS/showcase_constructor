import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("showcases", sa.Column("public_id", sa.String(length=64), nullable=True))
    op.add_column(
        "showcases",
        sa.Column(
            "publication_version",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.add_column(
        "showcases",
        sa.Column("active_published_snapshot_internal_id", sa.BigInteger(), nullable=True),
    )
    op.create_unique_constraint("uq_showcases_public_id", "showcases", ["public_id"])

    op.create_table(
        "published_showcase_snapshots",
        sa.Column("internal_id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("showcase_internal_id", sa.BigInteger(), nullable=False),
        sa.Column("showcase_id", sa.String(length=64), nullable=False),
        sa.Column("public_id", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=128), nullable=False),
        sa.Column("created_by_partner_id", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["showcase_internal_id"],
            ["showcases.internal_id"],
            name="fk_published_showcase_snapshots_showcase_internal_id_showcases",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("internal_id", name="pk_published_showcase_snapshots"),
        sa.UniqueConstraint(
            "showcase_id",
            "version",
            name="uq_published_showcase_snapshots_showcase_id_version",
        ),
        sa.UniqueConstraint(
            "public_id",
            "version",
            name="uq_published_showcase_snapshots_public_id_version",
        ),
    )
    op.create_index(
        "ix_published_showcase_snapshots_public_id",
        "published_showcase_snapshots",
        ["public_id"],
    )

    op.create_foreign_key(
        "fk_showcases_active_published_snapshot_internal_id_snapshots",
        "showcases",
        "published_showcase_snapshots",
        ["active_published_snapshot_internal_id"],
        ["internal_id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "published_route_bindings",
        sa.Column("internal_id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("showcase_internal_id", sa.BigInteger(), nullable=False),
        sa.Column("showcase_id", sa.String(length=64), nullable=False),
        sa.Column("public_id", sa.String(length=64), nullable=False),
        sa.Column("host", sa.String(length=253), nullable=False),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["showcase_internal_id"],
            ["showcases.internal_id"],
            name="fk_published_route_bindings_showcase_internal_id_showcases",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("internal_id", name="pk_published_route_bindings"),
        sa.UniqueConstraint("host", "path", name="uq_published_route_bindings_host_path"),
    )
    op.create_index(
        "ix_published_route_bindings_public_id_active",
        "published_route_bindings",
        ["public_id", "active"],
    )

    op.create_table(
        "showcase_audit_records",
        sa.Column("internal_id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("showcase_internal_id", sa.BigInteger(), nullable=False),
        sa.Column("showcase_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("actor_user_id", sa.String(length=128), nullable=False),
        sa.Column("actor_partner_id", sa.String(length=128), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["showcase_internal_id"],
            ["showcases.internal_id"],
            name="fk_showcase_audit_records_showcase_internal_id_showcases",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("internal_id", name="pk_showcase_audit_records"),
    )
    op.create_index(
        "ix_showcase_audit_records_showcase_id_created_at",
        "showcase_audit_records",
        ["showcase_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_showcase_audit_records_showcase_id_created_at",
        table_name="showcase_audit_records",
    )
    op.drop_table("showcase_audit_records")
    op.drop_index(
        "ix_published_route_bindings_public_id_active",
        table_name="published_route_bindings",
    )
    op.drop_table("published_route_bindings")
    op.drop_constraint(
        "fk_showcases_active_published_snapshot_internal_id_snapshots",
        "showcases",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_published_showcase_snapshots_public_id",
        table_name="published_showcase_snapshots",
    )
    op.drop_table("published_showcase_snapshots")
    op.drop_constraint("uq_showcases_public_id", "showcases", type_="unique")
    op.drop_column("showcases", "active_published_snapshot_internal_id")
    op.drop_column("showcases", "publication_version")
    op.drop_column("showcases", "public_id")
