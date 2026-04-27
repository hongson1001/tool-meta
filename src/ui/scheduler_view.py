"""Tab xem/sửa/hủy lịch đăng."""
import json

import pandas as pd
import streamlit as st

from src.database import get_session
from src.models import Post
from src.services.scheduler import cancel_scheduled


def render() -> None:
    st.header("⏰ Lịch Đăng")

    with get_session() as db:
        scheduled = db.query(Post).filter(
            Post.status == "pending",
            Post.scheduled_at.isnot(None),
        ).order_by(Post.scheduled_at).all()

    if not scheduled:
        st.info("Chưa có bài nào được đặt lịch.")
        return

    df = pd.DataFrame([
        {
            "ID": p.id,
            "Caption": (p.caption[:80] + "...") if len(p.caption) > 80 else p.caption,
            "Pages": len(json.loads(p.target_page_ids or "[]")),
            "Scheduled at": p.scheduled_at.strftime("%Y-%m-%d %H:%M") if p.scheduled_at else "—",
            "Sheet row": p.sheet_row_index or "—",
            "Status": p.status,
        }
        for p in scheduled
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    target_id = st.number_input("ID bài muốn hủy", min_value=1, step=1)
    if st.button("❌ Hủy lịch", type="secondary"):
        with get_session() as db:
            post = db.query(Post).filter(Post.id == int(target_id)).first()
            if not post:
                st.error("Không tìm thấy bài.")
                return
            cancel_scheduled(post.id)
            post.status = "cancelled"
            db.commit()
        st.success(f"Đã hủy lịch bài #{int(target_id)}")
        st.rerun()
