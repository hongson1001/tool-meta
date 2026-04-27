"""Tab quản lý fanpage — view list + thao tác per-page.

Note: chức năng connect tài khoản FB + import pages đã chuyển sang tab "Tài khoản FB".
Tab này chỉ để xem danh sách + thao tác active/verify/delete trên page đã import.
"""
import pandas as pd
import streamlit as st

from src.database import get_session
from src.models import Account, Page
from src.services import fb_client


def _mask_token(token: str) -> str:
    if not token or len(token) < 12:
        return "***"
    return token[:6] + "..." + token[-4:]


def _add_or_update_page(page_id: str, name: str, access_token: str, owner_label: str) -> str:
    with get_session() as db:
        existing = db.query(Page).filter(Page.page_id == page_id).first()
        if existing:
            existing.name = name
            existing.access_token = access_token
            existing.owner_account_label = owner_label
            existing.token_expired = False
            db.commit()
            return "updated"
        db.add(Page(
            page_id=page_id,
            name=name,
            access_token=access_token,
            owner_account_label=owner_label,
        ))
        db.commit()
        return "created"


def render() -> None:
    st.header("📋 Quản lý Fanpage")
    st.caption(
        "Xem các fanpage đã import qua tab **Tài khoản FB**. "
        "Mỗi page hiển thị tài khoản FB chủ + token + trạng thái."
    )

    tab_list, tab_add_one = st.tabs([
        "📑 Danh sách",
        "➕ Thêm thủ công (advanced)",
    ])

    with tab_list:
        _render_list()

    with tab_add_one:
        _render_add_one()


def _render_list() -> None:
    with get_session() as db:
        rows = db.query(Page, Account).outerjoin(Account, Page.account_id == Account.id).order_by(
            Account.name, Page.name
        ).all()

    pages = [r[0] for r in rows]
    account_name_by_page = {r[0].id: (r[1].name if r[1] else r[0].owner_account_label) for r in rows}

    if not pages:
        st.info(
            "Chưa có page nào. Vào tab **Tài khoản FB** → bấm **'➕ Thêm tài khoản FB'** "
            "để connect tài khoản và import pages tự động."
        )
        return

    df = pd.DataFrame([
        {
            "ID": p.id,
            "Page ID": p.page_id,
            "Tên page": p.name,
            "Tài khoản": account_name_by_page.get(p.id) or "(legacy)",
            "Token": _mask_token(p.access_token),
            "Active": "✅" if p.is_active else "⏸️",
            "Token expired": "⚠️" if p.token_expired else "",
            "Ngày thêm": p.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for p in pages
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

    n_active = sum(1 for p in pages if p.is_active)
    n_expired = sum(1 for p in pages if p.token_expired)
    st.caption(f"Tổng: **{len(pages)}** page · Active: **{n_active}** · Expired: **{n_expired}**")

    st.divider()
    st.subheader("Thao tác")

    col1, col2, col3 = st.columns(3)
    with col1:
        target_id = st.number_input("ID page (cột ID trong bảng)", min_value=1, step=1)
    with col2:
        action = st.selectbox("Hành động", ["Toggle active", "Verify token", "Xóa"])
    with col3:
        st.write("")
        st.write("")
        if st.button("Thực hiện", use_container_width=True):
            _do_action(int(target_id), action)


def _do_action(target_id: int, action: str) -> None:
    with get_session() as db:
        page = db.query(Page).filter(Page.id == target_id).first()
        if not page:
            st.error(f"Không tìm thấy page ID={target_id}")
            return

        if action == "Toggle active":
            page.is_active = not page.is_active
            db.commit()
            st.success(f"Đã {'bật' if page.is_active else 'tắt'} page **{page.name}**")
            st.rerun()

        elif action == "Verify token":
            try:
                info = fb_client.verify_page_token(page.page_id, page.access_token)
                page.token_expired = False
                page.name = info.get("name", page.name)
                db.commit()
                st.success(f"✅ Token OK — {info.get('name')} ({info.get('id')})")
            except fb_client.FbApiError as e:
                if e.code in (190, 102):
                    page.token_expired = True
                    db.commit()
                st.error(f"❌ {e}")

        elif action == "Xóa":
            db.delete(page)
            db.commit()
            st.success(f"Đã xóa page **{page.name}**")
            st.rerun()


def _render_add_one() -> None:
    st.write("Thêm 1 page khi đã có **Page Access Token** sẵn.")
    with st.form("add_one_page"):
        col1, col2 = st.columns(2)
        with col1:
            page_id = st.text_input("Page ID", placeholder="123456789012345")
            name = st.text_input("Tên page", placeholder="Shop Son ABC")
        with col2:
            owner_label = st.text_input("Thuộc tài khoản", placeholder="Tài khoản 1 - Sơn")
            verify = st.checkbox("Verify token với FB trước khi lưu", value=True)
        access_token = st.text_area("Page Access Token", height=100)
        submitted = st.form_submit_button("Thêm page", type="primary")

    if not submitted:
        return

    if not page_id or not access_token:
        st.error("Page ID và Access Token là bắt buộc.")
        return

    final_name = name.strip()
    if verify:
        try:
            info = fb_client.verify_page_token(page_id.strip(), access_token.strip())
            final_name = info.get("name") or final_name or page_id
            st.success(f"✅ Token OK — page: **{info.get('name')}**")
        except fb_client.FbApiError as e:
            st.error(f"❌ Verify thất bại: {e}")
            return

    result = _add_or_update_page(
        page_id.strip(),
        final_name or page_id.strip(),
        access_token.strip(),
        owner_label.strip(),
    )
    st.success(f"Đã {'cập nhật' if result == 'updated' else 'thêm'} page **{final_name}**")
