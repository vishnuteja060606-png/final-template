from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, get_utc_now

class EmbeddingRecord(Base):
    """
    Sidecar table storing vector embeddings for creators, portfolio items, and briefs.
    Ensures zero breaking changes to existing core tables while supporting local ONNX vector retrieval.
    """
    __tablename__ = "embedding_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # 'creator', 'job', 'portfolio'
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(100), default="bge-small-en-v1.5")
    embedding_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON-encoded array of 384 floats
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # MD5 to skip redundant re-embedding
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    __table_args__ = (
        Index("idx_embedding_entity", "entity_type", "entity_id", unique=True),
    )


class ExtractedEntity(Base):
    """
    Sidecar table storing NER-extracted and canonicalized entities with provenance tracking.
    """
    __tablename__ = "extracted_entities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # 'creator', 'job', 'portfolio'
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # 'tool', 'skill', 'style', 'format', 'license', 'budget'
    raw_value: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_value: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    provenance: Mapped[str] = mapped_column(String(50), default="creator_claim")  # 'creator_claim', 'platform_verified', 'brief_requirement'
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)

    __table_args__ = (
        Index("idx_entity_lookup", "entity_type", "entity_id", "category"),
    )
