from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UsageRecord(Base):
    """One row per (user, billing period). Period format: YYYY-MM."""

    __tablename__ = "usage_records"
    __table_args__ = (UniqueConstraint("user_id", "period", name="uq_usage_user_period"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    period: Mapped[str] = mapped_column(String(7), nullable=False)  # "2026-03"
    queries_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship()  # noqa: F821
