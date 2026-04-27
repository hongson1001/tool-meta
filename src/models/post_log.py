"""Model log chi tiết từng page trong 1 campaign."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class PostLog(Base):
    __tablename__ = "post_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id"), index=True)
    batch_index: Mapped[int] = mapped_column(Integer, default=0)
    applied_caption: Mapped[str] = mapped_column(Text, default="")
    fb_post_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    fb_post_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comment_posted: Mapped[bool] = mapped_column(Boolean, default=False)
    fb_comment_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    posted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
