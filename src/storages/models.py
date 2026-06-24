from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core.showcases.schemas import (
    AdminShowcase,
    AdminShowcaseDraft,
    AdminShowcaseDraftBlock,
    AdminShowcaseDraftOffer,
    JsonObject,
    JsonValue,
)


class Base(DeclarativeBase):
    pass


class AdminShowcaseModel(Base):
    __tablename__ = "showcases"
    __table_args__ = (
        PrimaryKeyConstraint("internal_id", name="pk_showcases"),
        UniqueConstraint("id", name="uq_showcases_id"),
        Index("ix_showcases_owner_partner_id", "owner_partner_id"),
    )

    internal_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    id: Mapped[str] = mapped_column(String(length=64), nullable=False)
    owner_partner_id: Mapped[str] = mapped_column(String(length=128), nullable=False)
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    draft_settings: Mapped[JsonObject] = mapped_column(JSONB, nullable=False, default=dict)
    published_snapshot: Mapped[JsonObject | None] = mapped_column(JSONB, nullable=True)

    def to_domain(self) -> AdminShowcase:
        return AdminShowcase(
            id=self.id,
            owner_partner_id=self.owner_partner_id,
            title=self.title,
        )

    def to_draft_domain(self) -> AdminShowcaseDraft:
        return AdminShowcaseDraft(
            id=self.id,
            owner_partner_id=self.owner_partner_id,
            title=self.title,
            settings=self.draft_settings,
            published_snapshot=self.published_snapshot,
        )


class AdminShowcaseDraftBlockModel(Base):
    __tablename__ = "draft_blocks"
    __table_args__ = (
        PrimaryKeyConstraint("internal_id", name="pk_draft_blocks"),
        UniqueConstraint("showcase_id", "block_id", name="uq_draft_blocks_showcase_id_block_id"),
        Index("ix_draft_blocks_showcase_id_draft_order", "showcase_id", "draft_order"),
    )

    internal_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    showcase_internal_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "showcases.internal_id",
            name="fk_draft_blocks_showcase_internal_id_showcases",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    showcase_id: Mapped[str] = mapped_column(String(length=64), nullable=False)
    block_id: Mapped[str] = mapped_column(String(length=64), nullable=False)
    type: Mapped[str] = mapped_column(String(length=32), nullable=False)
    draft_order: Mapped[int] = mapped_column(Integer, nullable=False)
    visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    title: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    subtitle: Mapped[str | None] = mapped_column(Text, nullable=True)
    desktop_settings: Mapped[JsonObject] = mapped_column(JSONB, nullable=False, default=dict)
    mobile_settings: Mapped[JsonObject] = mapped_column(JSONB, nullable=False, default=dict)
    data: Mapped[JsonObject] = mapped_column(JSONB, nullable=False, default=dict)

    def to_domain(self) -> AdminShowcaseDraftBlock:
        return AdminShowcaseDraftBlock(
            id=self.block_id,
            showcase_id=self.showcase_id,
            type=self.type,
            order=self.draft_order,
            visible=self.visible,
            title=self.title,
            subtitle=self.subtitle,
            desktop_settings=self.desktop_settings,
            mobile_settings=self.mobile_settings,
            data=self.data,
        )


class AdminShowcaseDraftOfferModel(Base):
    __tablename__ = "draft_offers"
    __table_args__ = (
        PrimaryKeyConstraint("internal_id", name="pk_draft_offers"),
        UniqueConstraint("showcase_id", "offer_id", name="uq_draft_offers_showcase_id_offer_id"),
        Index(
            "ix_draft_offers_showcase_id_block_id_manual_order",
            "showcase_id",
            "block_id",
            "manual_order",
        ),
    )

    internal_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    showcase_internal_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "showcases.internal_id",
            name="fk_draft_offers_showcase_internal_id_showcases",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    showcase_id: Mapped[str] = mapped_column(String(length=64), nullable=False)
    offer_id: Mapped[str] = mapped_column(String(length=64), nullable=False)
    block_id: Mapped[str | None] = mapped_column(String(length=64), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    manual_order: Mapped[int] = mapped_column(Integer, nullable=False)
    cta_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    usp_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    fields: Mapped[list[JsonValue]] = mapped_column(JSONB, nullable=False, default=list)
    categories: Mapped[list[JsonValue]] = mapped_column(JSONB, nullable=False, default=list)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    rounded_logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    site_name: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    cpa_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    legal_entity: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    inn: Mapped[str | None] = mapped_column(String(length=32), nullable=True)
    erid: Mapped[str | None] = mapped_column(String(length=128), nullable=True)
    data: Mapped[JsonObject] = mapped_column(JSONB, nullable=False, default=dict)

    def to_domain(self) -> AdminShowcaseDraftOffer:
        return AdminShowcaseDraftOffer(
            id=self.offer_id,
            showcase_id=self.showcase_id,
            block_id=self.block_id,
            enabled=self.enabled,
            manual_order=self.manual_order,
            cta_text=self.cta_text,
            usp_text=self.usp_text,
            fields=self.fields,
            categories=self.categories,
            logo_url=self.logo_url,
            rounded_logo_url=self.rounded_logo_url,
            display_name=self.display_name,
            site_name=self.site_name,
            cpa_url=self.cpa_url,
            legal_entity=self.legal_entity,
            inn=self.inn,
            erid=self.erid,
            data=self.data,
        )
