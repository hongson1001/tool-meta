"""Tab tạo bài đăng từ Sheet row."""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import BATCH_SIZE, GOOGLE_CREDENTIALS_PATH
from src.database import get_session
from src.models import Account, Page, Post, PostLog, SheetsConfig

STATUS_LABEL = {
    "pending": "⏳ Chờ",
    "queued": "⏳ Đợi delay",
    "posting": "📝 Đang đăng bài",
    "waiting_comment": "⏸️ Đợi delay comment",
    "commenting": "💬 Đang comment",
    "success": "✅ Xong",
    "failed": "❌ Lỗi",
}
from src.services import sheets_client
from src.services.batch_runner import run_in_background
from src.services.scheduler import schedule_post
from src.services.variant import build_final_caption


def render() -> None:
    st.header("✏️ Tạo Bài Đăng")

    if "watching_post_id" in st.session_state:
        _render_progress()
        st.divider()

    with get_session() as db:
        cfg = db.query(SheetsConfig).filter(SheetsConfig.is_active == True).first()  # noqa: E712
        page_rows = db.query(Page, Account).outerjoin(
            Account, Page.account_id == Account.id
        ).filter(
            Page.is_active == True,  # noqa: E712
            Page.token_expired == False,  # noqa: E712
        ).order_by(Account.name, Page.name).all()
        active_pages = [r[0] for r in page_rows]
        page_account_name = {
            r[0].id: (r[1].name if r[1] else r[0].owner_account_label or "(legacy)")
            for r in page_rows
        }

    if not cfg:
        st.warning("Chưa có config Google Sheet. Vào tab **Google Sheet** để config trước.")
        return
    if not active_pages:
        st.warning(
            "Chưa có Page active. Vào tab **Tài khoản FB** để connect tài khoản và import pages."
        )
        return

    pages_by_account: dict[str, list[Page]] = {}
    for p in active_pages:
        acc_name = page_account_name.get(p.id, "(legacy)")
        pages_by_account.setdefault(acc_name, []).append(p)

    st.subheader("1. Chọn nguồn bài từ Sheet")

    if st.button("🔄 Refresh Sheet", type="secondary"):
        st.session_state.pop("pending_rows", None)

    if "pending_rows" not in st.session_state:
        try:
            st.session_state["pending_rows"] = sheets_client.fetch_pending_posts(
                Path(GOOGLE_CREDENTIALS_PATH), cfg.sheet_id, cfg.tab_name
            )
        except Exception as e:
            st.error(f"❌ Không đọc được Sheet: {e}")
            return

    rows = st.session_state["pending_rows"]
    if not rows:
        st.info("Sheet không có row pending (used = FALSE) nào.")
        return

    df = pd.DataFrame([
        {
            "Row": r.row_index,
            "Caption": (r.caption[:80] + "...") if len(r.caption) > 80 else r.caption,
            "Video": r.video_link,
            "Shopee": r.shopee_link,
            "Comment": (r.comment_text[:60] + "...") if len(r.comment_text) > 60 else r.comment_text,
        }
        for r in rows
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

    row_options = {f"Row {r.row_index} — {r.caption[:60]}": r for r in rows}
    selected_label = st.selectbox("Chọn 1 row để đăng", list(row_options.keys()))
    selected_row = row_options[selected_label]

    st.divider()
    st.subheader("2. Form đăng bài")

    col1, col2 = st.columns(2)
    with col1:
        caption = st.text_area(
            "Caption", value=selected_row.caption, height=120, key=f"caption_{selected_row.row_index}"
        )
        video_link = st.text_input(
            "Video link", value=selected_row.video_link, key=f"video_{selected_row.row_index}"
        )
    with col2:
        comment_text = st.text_area(
            "Comment text", value=selected_row.comment_text, height=120, key=f"comment_{selected_row.row_index}"
        )
        shopee_link = st.text_input(
            "Shopee link", value=selected_row.shopee_link, key=f"shopee_{selected_row.row_index}"
        )

    all_page_labels = {
        f"[{page_account_name.get(p.id, '?')}] {p.name}": p for p in active_pages
    }

    st.markdown(
        f"**Pages đăng lên** — tổng **{len(active_pages)}** active "
        f"(thuộc **{len(pages_by_account)}** tài khoản FB)"
    )

    filter_cols = st.columns([2, 3])
    with filter_cols[0]:
        filter_mode = st.radio(
            "Chọn nhanh",
            ["Tất cả tài khoản", "Chỉ 1 tài khoản"],
            horizontal=True,
            key=f"page_filter_mode_{selected_row.row_index}",
        )
    if filter_mode == "Chỉ 1 tài khoản":
        with filter_cols[1]:
            selected_account = st.selectbox(
                "Chọn tài khoản",
                options=list(pages_by_account.keys()),
                key=f"page_filter_acc_{selected_row.row_index}",
            )
        default_pages = [
            f"[{selected_account}] {p.name}" for p in pages_by_account[selected_account]
        ]
    else:
        default_pages = list(all_page_labels.keys())

    selected_page_labels = st.multiselect(
        "Multi-select (có thể tự chỉnh)",
        options=list(all_page_labels.keys()),
        default=default_pages,
        key=f"page_select_{selected_row.row_index}",
    )

    if selected_page_labels:
        counts: dict[str, int] = {}
        for lbl in selected_page_labels:
            p = all_page_labels[lbl]
            acc_name = page_account_name.get(p.id, "?")
            counts[acc_name] = counts.get(acc_name, 0) + 1
        badge = " · ".join([f"**{k}**: {v}" for k, v in counts.items()])
        st.caption(f"Đã chọn **{len(selected_page_labels)}** pages — {badge}")

    col3, col4 = st.columns(2)
    with col3:
        variant_on = st.toggle("Biến thể nội dung (khuyến nghị ON)", value=True)
    with col4:
        schedule_mode = st.radio(
            "Chế độ", ["⚡ Đăng ngay", "⏰ Đặt lịch"], horizontal=True
        )

    scheduled_at = None
    if schedule_mode == "⏰ Đặt lịch":
        col5, col6 = st.columns(2)
        with col5:
            date_pick = st.date_input("Ngày đăng", value=datetime.now().date())
        with col6:
            time_pick = st.time_input(
                "Giờ đăng", value=(datetime.now() + timedelta(minutes=30)).time()
            )
        scheduled_at = datetime.combine(date_pick, time_pick)

    dry_run = st.checkbox("🧪 Dry Run (chỉ log, không gọi FB API)", value=False)

    submit = st.button("🚀 Xác nhận", type="primary", use_container_width=False)

    if not submit:
        return

    if not selected_page_labels:
        st.error("Cần chọn ít nhất 1 page.")
        return

    selected_pages = [all_page_labels[lbl] for lbl in selected_page_labels]
    page_db_ids = [p.id for p in selected_pages]
    n_pages = len(selected_pages)
    n_batches = (n_pages + BATCH_SIZE - 1) // BATCH_SIZE

    with get_session() as db:
        new_post = Post(
            sheet_row_index=selected_row.row_index,
            caption=caption,
            video_link=video_link,
            shopee_link=shopee_link,
            comment_text=comment_text,
            target_page_ids=json.dumps(page_db_ids),
            scheduled_at=scheduled_at,
            variant_mode="auto_variant" if variant_on else "identical",
            status="pending",
        )
        db.add(new_post)
        db.commit()
        post_id = new_post.id

    sample = build_final_caption(
        caption, video_link, "auto_variant" if variant_on else "identical"
    )
    with st.expander("👀 Preview caption (1 version mẫu)", expanded=True):
        st.code(sample)

    if schedule_mode == "⚡ Đăng ngay":
        run_in_background(post_id, dry_run=dry_run)
        st.success(
            f"🚀 Đã start campaign #{post_id} — {n_pages} page / {n_batches} batch / "
            f"~{n_batches * 4} phút."
        )
        st.session_state["watching_post_id"] = post_id
        st.session_state.pop("pending_rows", None)
    else:
        schedule_post(post_id, scheduled_at)
        st.success(f"⏰ Đã đặt lịch campaign #{post_id} vào {scheduled_at}")
        st.session_state.pop("pending_rows", None)

    st.rerun()


def _render_progress() -> None:
    pid = st.session_state.get("watching_post_id")
    if not pid:
        return

    with get_session() as db:
        post = db.query(Post).filter(Post.id == pid).first()
        if not post:
            del st.session_state["watching_post_id"]
            return
        page_db_ids = json.loads(post.target_page_ids or "[]")
        total = len(page_db_ids)
        rows = db.query(PostLog, Page).join(
            Page, PostLog.page_id == Page.id
        ).filter(PostLog.post_id == pid).order_by(PostLog.id).all()

    logs = [r[0] for r in rows]
    page_name_by_log: dict[int, str] = {r[0].id: r[1].name for r in rows}

    success_count = sum(1 for l in logs if l.status == "success")
    failed_count = sum(1 for l in logs if l.status == "failed")
    completed = success_count + failed_count
    is_done = post.status in ("success", "partial", "failed", "cancelled")

    prev_key = f"prev_log_status_{pid}"
    prev_statuses: dict[int, str] = st.session_state.get(prev_key, {})
    for log in logs:
        prev = prev_statuses.get(log.id)
        if prev != log.status:
            page_name = page_name_by_log.get(log.id, f"Page #{log.page_id}")
            if log.status == "success":
                st.toast(f"✅ {page_name} đăng xong", icon="✅")
            elif log.status == "failed":
                err_short = (log.error_message or "lỗi")[:60]
                st.toast(f"❌ {page_name} lỗi: {err_short}", icon="❌")
            elif log.status == "posting" and prev not in (None, "pending"):
                st.toast(f"📝 {page_name} đang đăng bài", icon="📝")
            elif log.status == "waiting_comment":
                st.toast(f"⏸️ {page_name} đợi comment delay", icon="⏸️")
            elif log.status == "commenting":
                st.toast(f"💬 {page_name} đang comment", icon="💬")
    st.session_state[prev_key] = {l.id: l.status for l in logs}

    st.subheader(f"📡 Campaign #{pid} — status: **{post.status}**")

    if post.progress_step:
        elapsed = ""
        if post.progress_updated_at:
            secs = int((datetime.utcnow() - post.progress_updated_at).total_seconds())
            if secs > 0:
                elapsed = f"  \n_đã ở step này {secs}s_"
        if is_done:
            st.success(f"**{post.progress_step}**{elapsed}")
        else:
            st.info(f"**{post.progress_step}**{elapsed}")

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn1:
        if st.button("🔄 Refresh status", use_container_width=True):
            st.rerun()
    with col_btn2:
        auto_refresh = st.toggle(
            "Auto refresh 5s", value=not is_done, disabled=is_done, key=f"auto_refresh_{pid}"
        )
    with col_btn3:
        if st.button("✖️ Đóng theo dõi", use_container_width=True):
            st.session_state.pop(f"auto_refresh_{pid}", None)
            del st.session_state["watching_post_id"]
            st.rerun()

    st.progress(completed / max(total, 1))
    c1, c2, c3 = st.columns(3)
    c1.metric("Hoàn tất", f"{completed}/{total}")
    c2.metric("Thành công", success_count)
    c3.metric("Lỗi", failed_count)

    if logs:
        with st.expander(f"Chi tiết log ({len(logs)} dòng)", expanded=True):
            df = pd.DataFrame([{
                "Page": page_name_by_log.get(l.id, f"#{l.page_id}"),
                "Batch": l.batch_index,
                "Status": STATUS_LABEL.get(l.status, l.status),
                "FB Post URL": l.fb_post_url or "—",
                "Comment": "✅" if l.comment_posted else "—",
                "Error": l.error_message or "",
                "At": l.posted_at.strftime("%H:%M:%S"),
            } for l in logs])
            st.dataframe(df, use_container_width=True, hide_index=True)

    if is_done:
        st.success(f"✅ Campaign #{pid} hoàn tất với status: **{post.status}**")
    elif auto_refresh:
        time.sleep(5)
        st.rerun()
