"""Tab lịch sử + dashboard."""
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import func

from src.database import get_session
from src.models import Page, Post, PostLog


def render() -> None:
    st.header("📜 Lịch Sử & Dashboard")

    tab_dashboard, tab_history = st.tabs(["📊 Dashboard", "📜 Lịch sử"])

    with tab_dashboard:
        _render_dashboard()
    with tab_history:
        _render_history()


def _render_dashboard() -> None:
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)

    with get_session() as db:
        today_count = db.query(PostLog).filter(PostLog.posted_at >= today_start).count()
        week_count = db.query(PostLog).filter(PostLog.posted_at >= week_start).count()
        month_count = db.query(PostLog).filter(PostLog.posted_at >= month_start).count()
        total = db.query(PostLog).count()
        success_count = db.query(PostLog).filter(PostLog.status == "success").count()
        failed_count = db.query(PostLog).filter(PostLog.status == "failed").count()
        comments_count = db.query(PostLog).filter(PostLog.comment_posted == True).count()  # noqa: E712

        rate = (success_count / total * 100) if total > 0 else 0.0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📅 Hôm nay", today_count)
        c2.metric("📆 7 ngày", week_count)
        c3.metric("🗓️ 30 ngày", month_count)
        c4.metric("✅ Tỷ lệ thành công", f"{rate:.1f}%")

        c5, c6, c7 = st.columns(3)
        c5.metric("Total success", success_count)
        c6.metric("Total failed", failed_count)
        c7.metric("Tổng comments", comments_count)

        st.divider()
        st.subheader("📈 Số bài 7 ngày gần nhất")

        rows = db.query(
            func.date(PostLog.posted_at).label("day"),
            func.count(PostLog.id).label("count"),
        ).filter(PostLog.posted_at >= week_start).group_by("day").all()

        if rows:
            chart_df = pd.DataFrame([(r.day, r.count) for r in rows], columns=["Ngày", "Số bài"])
            fig = px.bar(chart_df, x="Ngày", y="Số bài")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu trong 7 ngày.")

        st.subheader("🏆 Top 5 page hoạt động (30 ngày)")
        top = db.query(
            Page.name,
            Page.owner_account_label,
            func.count(PostLog.id).label("count"),
        ).join(PostLog, PostLog.page_id == Page.id).filter(
            PostLog.status == "success",
            PostLog.posted_at >= month_start,
        ).group_by(Page.id).order_by(func.count(PostLog.id).desc()).limit(5).all()

        if top:
            top_df = pd.DataFrame(
                [(t.name, t.owner_account_label or "—", t.count) for t in top],
                columns=["Page", "Tài khoản", "Số bài"],
            )
            st.dataframe(top_df, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có dữ liệu.")


def _render_history() -> None:
    col1, col2, col3 = st.columns(3)
    with col1:
        date_from = st.date_input(
            "Từ ngày", value=datetime.utcnow().date() - timedelta(days=30)
        )
    with col2:
        date_to = st.date_input("Đến ngày", value=datetime.utcnow().date())
    with col3:
        status_filter = st.selectbox(
            "Status", ["all", "success", "partial", "failed", "cancelled", "pending", "running"]
        )

    search = st.text_input("Search caption / Shopee link")

    with get_session() as db:
        q = db.query(Post)
        q = q.filter(Post.created_at >= datetime.combine(date_from, datetime.min.time()))
        q = q.filter(Post.created_at <= datetime.combine(date_to, datetime.max.time()))
        if status_filter != "all":
            q = q.filter(Post.status == status_filter)
        if search:
            like = f"%{search}%"
            q = q.filter((Post.caption.like(like)) | (Post.shopee_link.like(like)))
        posts = q.order_by(Post.created_at.desc()).limit(200).all()

        if not posts:
            st.info("Không có dữ liệu.")
            return

        rows_data = []
        for p in posts:
            success_n = db.query(PostLog).filter(
                PostLog.post_id == p.id, PostLog.status == "success"
            ).count()
            total_n = db.query(PostLog).filter(PostLog.post_id == p.id).count()
            rows_data.append({
                "ID": p.id,
                "Caption": (p.caption[:80] + "...") if len(p.caption) > 80 else p.caption,
                "Sheet row": p.sheet_row_index or "—",
                "Success/Total": f"{success_n}/{total_n}",
                "Status": p.status,
                "Created": p.created_at.strftime("%Y-%m-%d %H:%M"),
            })
        df = pd.DataFrame(rows_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"{len(posts)} bài (tối đa 200 dòng)")

        col_dl, col_id = st.columns(2)
        with col_dl:
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 Export CSV",
                data=csv,
                file_name=f"history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_id:
            view_id = st.number_input("Xem chi tiết bài ID", min_value=1, step=1)
            if st.button("🔍 Xem chi tiết", use_container_width=True):
                st.session_state["history_view_id"] = int(view_id)

    if "history_view_id" in st.session_state:
        st.divider()
        _show_detail(st.session_state["history_view_id"])


def _show_detail(post_id: int) -> None:
    with get_session() as db:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            st.error("Không tìm thấy bài.")
            return
        logs = db.query(PostLog, Page).join(Page, PostLog.page_id == Page.id).filter(
            PostLog.post_id == post.id
        ).all()

    st.markdown(f"### 🔍 Chi tiết bài #{post.id}")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Caption gốc**: {post.caption}")
        st.markdown(f"**Video**: {post.video_link or '—'}")
        st.markdown(f"**Shopee**: {post.shopee_link or '—'}")
    with c2:
        st.markdown(f"**Comment**: {post.comment_text or '—'}")
        st.markdown(f"**Sheet row**: {post.sheet_row_index or '—'}")
        st.markdown(f"**Status**: {post.status}")

    if logs:
        rows = [{
            "Page": page.name,
            "Tài khoản": page.owner_account_label or "—",
            "Status": "✅" if log.status == "success" else "❌",
            "FB URL": log.fb_post_url or "—",
            "Comment": "✅" if log.comment_posted else "—",
            "Error": log.error_message or "",
            "At": log.posted_at.strftime("%Y-%m-%d %H:%M:%S"),
        } for log, page in logs]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có log.")

    if st.button("Đóng chi tiết"):
        del st.session_state["history_view_id"]
        st.rerun()
