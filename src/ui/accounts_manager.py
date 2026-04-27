"""Tab quản lý tài khoản Facebook — connect, list, refresh, logout."""
import streamlit as st

from src.config import FB_APP_ID, FB_APP_SECRET, OAUTH_BACKEND_URL
from src.database import get_session
from src.models import Account, Page
from src.services import account_service, fb_client, oauth_local


def render() -> None:
    st.header("👥 Tài khoản Facebook")

    if not FB_APP_ID:
        st.error(
            "❌ Chưa cấu hình **FB_APP_ID** trong file `.env`. "
            "Hãy điền App ID từ Dashboard Facebook Developer rồi restart tool."
        )
        return

    if not OAUTH_BACKEND_URL and not FB_APP_SECRET:
        st.warning(
            "⚠️ Cần điền **FB_APP_SECRET** trong `.env` (cho dev mode) "
            "hoặc **OAUTH_BACKEND_URL** (cho production) để OAuth hoạt động."
        )

    st.write(
        "Connect các tài khoản Facebook quản lý fanpage của bạn. "
        "Bấm nút bên dưới, browser sẽ tự mở để bạn đăng nhập + cấp quyền."
    )

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        if st.button("➕ Thêm tài khoản FB", type="primary", use_container_width=True):
            _trigger_authorize()

    with col_info:
        st.caption(
            "💡 Mẹo: Để connect nhiều tài khoản FB khác nhau, "
            "logout FB trên browser hoặc dùng Chrome Incognito (Ctrl+Shift+N) "
            "trước khi bấm thêm tài khoản."
        )

    if "_oauth_result" in st.session_state:
        msg = st.session_state.pop("_oauth_result")
        st.success(msg)
    if "_oauth_error" in st.session_state:
        err = st.session_state.pop("_oauth_error")
        st.error(err)

    st.divider()

    with get_session() as db:
        accounts = db.query(Account).order_by(Account.created_at).all()

    if not accounts:
        st.info("Chưa có tài khoản nào. Bấm **'➕ Thêm tài khoản FB'** để bắt đầu.")
        return

    total_pages = 0
    with get_session() as db:
        total_pages = db.query(Page).filter(Page.is_active == True).count()  # noqa: E712

    st.markdown(
        f"### Đã connect **{len(accounts)}** tài khoản — tổng **{total_pages}** pages"
    )

    for acc in accounts:
        with get_session() as db:
            page_count = db.query(Page).filter(
                Page.account_id == acc.id, Page.is_active == True  # noqa: E712
            ).count()
            expired_count = db.query(Page).filter(
                Page.account_id == acc.id, Page.token_expired == True  # noqa: E712
            ).count()

        with st.container(border=True):
            col_info, col_actions = st.columns([3, 2])

            with col_info:
                st.markdown(f"#### 👤 {acc.name}")
                st.caption(f"Facebook User ID: `{acc.fb_user_id}`")

                badges = [f"📄 **{page_count}** pages"]
                if expired_count > 0:
                    badges.append(f"⚠️ {expired_count} token expired")
                if acc.token_expired:
                    badges.append("🔒 **User Token expired**")
                if acc.is_long_lived:
                    badges.append("🔐 Long-lived")
                else:
                    badges.append("⏰ Short-lived (1h)")
                st.write(" · ".join(badges))

                if acc.last_authorized_at:
                    st.caption(
                        f"Authorize lúc: {acc.last_authorized_at.strftime('%Y-%m-%d %H:%M')}"
                    )

            with col_actions:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🔄 Refresh pages", key=f"refresh_{acc.id}", use_container_width=True):
                        _refresh(acc.id)
                with c2:
                    if st.button("🔑 Re-auth", key=f"reauth_{acc.id}", use_container_width=True):
                        _trigger_authorize()

                if st.button("🚪 Logout", key=f"logout_{acc.id}", use_container_width=True, type="secondary"):
                    _logout(acc.id, acc.name)


def _trigger_authorize() -> None:
    try:
        with st.spinner(
            "🔗 Browser đã mở. Hãy login Facebook và cấp quyền cho App. "
            "Tool đang đợi callback..."
        ):
            result = account_service.authorize_new_account()

        st.session_state["_oauth_result"] = (
            f"✅ Đã connect **{result.name}** "
            f"({result.pages_count} pages, "
            f"{'long-lived 60 ngày' if result.is_long_lived else 'short-lived 1h'})"
        )
        st.rerun()
    except oauth_local.OAuthError as e:
        st.session_state["_oauth_error"] = f"❌ {e}"
        st.rerun()
    except account_service.AccountAuthError as e:
        st.session_state["_oauth_error"] = f"❌ {e}"
        st.rerun()
    except fb_client.FbApiError as e:
        st.session_state["_oauth_error"] = f"❌ FB API: {e}"
        st.rerun()
    except Exception as e:
        st.session_state["_oauth_error"] = f"❌ Lỗi không xác định: {type(e).__name__}: {e}"
        st.rerun()


def _refresh(account_id: int) -> None:
    try:
        with st.spinner("Đang fetch pages mới..."):
            count = account_service.sync_pages_for_account(account_id)
        st.session_state["_oauth_result"] = f"✅ Đã sync **{count}** pages"
    except fb_client.FbApiError as e:
        st.session_state["_oauth_error"] = f"❌ {e}. Hãy bấm Re-auth để authorize lại."
    except Exception as e:
        st.session_state["_oauth_error"] = f"❌ {type(e).__name__}: {e}"
    st.rerun()


def _logout(account_id: int, name: str) -> None:
    confirm_key = f"_confirm_logout_{account_id}"
    if not st.session_state.get(confirm_key):
        st.session_state[confirm_key] = True
        st.warning(f"⚠️ Bấm Logout 1 lần nữa để xác nhận xóa **{name}** + tất cả pages của tài khoản này khỏi tool.")
        st.rerun()
        return

    account_service.remove_account(account_id)
    st.session_state.pop(confirm_key, None)
    st.session_state["_oauth_result"] = f"✅ Đã logout **{name}** và xóa pages khỏi tool"
    st.rerun()
