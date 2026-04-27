"""Model bài đăng (1 row Sheet = 1 post campaign)."""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sheet_row_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    caption: Mapped[str] = mapped_column(Text)
    video_link: Mapped[str] = mapped_column(Text, default="")
    shopee_link: Mapped[str] = mapped_column(Text, default="")
    comment_text: Mapped[str] = mapped_column(Text, default="")
    target_page_ids: Mapped[str] = mapped_column(Text, default="[]")
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    variant_mode: Mapped[str] = mapped_column(String(32), default="auto_variant")
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    progress_step: Mapped[str] = mapped_column(String(255), default="")
    progress_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
