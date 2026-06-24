import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "showcases",
        sa.Column("internal_id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("owner_partner_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column(
            "draft_settings",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("published_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("internal_id", name="pk_showcases"),
        sa.UniqueConstraint("id", name="uq_showcases_id"),
    )
    op.create_index(
        "ix_showcases_owner_partner_id",
        "showcases",
        ["owner_partner_id"],
    )

    op.create_table(
        "draft_blocks",
        sa.Column("internal_id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("showcase_internal_id", sa.BigInteger(), nullable=False),
        sa.Column("showcase_id", sa.String(length=64), nullable=False),
        sa.Column("block_id", sa.String(length=64), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("draft_order", sa.Integer(), nullable=False),
        sa.Column("visible", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("subtitle", sa.Text(), nullable=True),
        sa.Column(
            "desktop_settings",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "mobile_settings",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "data",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["showcase_internal_id"],
            ["showcases.internal_id"],
            name="fk_draft_blocks_showcase_internal_id_showcases",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("internal_id", name="pk_draft_blocks"),
        sa.UniqueConstraint(
            "showcase_id",
            "block_id",
            name="uq_draft_blocks_showcase_id_block_id",
        ),
    )
    op.create_index(
        "ix_draft_blocks_showcase_id_draft_order",
        "draft_blocks",
        ["showcase_id", "draft_order"],
    )

    op.create_table(
        "draft_offers",
        sa.Column("internal_id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("showcase_internal_id", sa.BigInteger(), nullable=False),
        sa.Column("showcase_id", sa.String(length=64), nullable=False),
        sa.Column("offer_id", sa.String(length=64), nullable=False),
        sa.Column("block_id", sa.String(length=64), nullable=True),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("manual_order", sa.Integer(), nullable=False),
        sa.Column("cta_text", sa.Text(), nullable=True),
        sa.Column("usp_text", sa.Text(), nullable=True),
        sa.Column(
            "fields",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "categories",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("rounded_logo_url", sa.Text(), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("site_name", sa.String(length=255), nullable=True),
        sa.Column("cpa_url", sa.Text(), nullable=True),
        sa.Column("legal_entity", sa.String(length=255), nullable=True),
        sa.Column("inn", sa.String(length=32), nullable=True),
        sa.Column("erid", sa.String(length=128), nullable=True),
        sa.Column(
            "data",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["showcase_internal_id"],
            ["showcases.internal_id"],
            name="fk_draft_offers_showcase_internal_id_showcases",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("internal_id", name="pk_draft_offers"),
        sa.UniqueConstraint(
            "showcase_id",
            "offer_id",
            name="uq_draft_offers_showcase_id_offer_id",
        ),
    )
    op.create_index(
        "ix_draft_offers_showcase_id_block_id_manual_order",
        "draft_offers",
        ["showcase_id", "block_id", "manual_order"],
    )


def downgrade() -> None:
    op.drop_index("ix_draft_offers_showcase_id_block_id_manual_order", table_name="draft_offers")
    op.drop_table("draft_offers")
    op.drop_index("ix_draft_blocks_showcase_id_draft_order", table_name="draft_blocks")
    op.drop_table("draft_blocks")
    op.drop_index("ix_showcases_owner_partner_id", table_name="showcases")
    op.drop_table("showcases")
