"""Tab config Google Sheets."""
from datetime import datetime
from pathlib import Path

import streamlit as st

from src.config import GOOGLE_CREDENTIALS_PATH, GOOGLE_SHEET_ID, GOOGLE_SHEET_TAB
from src.database import get_session
from src.models import SheetsConfig
from src.services import sheets_client


def _save_config(sheet_id: str, tab_name: str) -> None:
    with get_session() as db:
        db.query(SheetsConfig).update({"is_active": False})
        db.add(SheetsConfig(
            sheet_id=sheet_id,
            tab_name=tab_name,
            is_active=True,
            last_synced_at=datetime.utcnow(),
        ))
        db.commit()


def render() -> None:
    st.header("📊 Google Sheet")

    with get_session() as db:
        cfg = db.query(SheetsConfig).filter(SheetsConfig.is_active == True).first()  # noqa: E712

    creds_path = Path(GOOGLE_CREDENTIALS_PATH)

    st.subheader("1. Service Account credentials")
    if creds_path.exists():
        st.success(f"✅ Đã có file credentials tại `{creds_path}`")
    else:
        st.warning(f"❌ Chưa có file `{creds_path}`. Upload bên dưới.")

    uploaded = st.file_uploader("Upload `credentials.json`", type=["json"])
    if uploaded:
        creds_path.parent.mkdir(parents=True, exist_ok=True)
        with creds_path.open("wb") as f:
            f.write(uploaded.read())
        st.success(f"Đã lưu tại `{creds_path}`")
        st.rerun()

    st.divider()
    st.subheader("2. Sheet ID + Tab name")

    default_sheet_id = cfg.sheet_id if cfg else GOOGLE_SHEET_ID
    default_tab = cfg.tab_name if cfg else GOOGLE_SHEET_TAB

    sheet_id = st.text_input(
        "Sheet ID (lấy từ URL Sheet)",
        value=default_sheet_id,
        placeholder="1AbC...xYz",
    )
    tab_name = st.text_input("Tên tab", value=default_tab or "posts")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Test connection", type="primary", use_container_width=True):
            if not creds_path.exists():
                st.error("Cần upload credentials.json trước.")
            elif not sheet_id.strip():
                st.error("Cần điền Sheet ID.")
            else:
                try:
                    info = sheets_client.verify_connection(
                        creds_path, sheet_id.strip(), tab_name.strip()
                    )
                    st.success(
                        f"✅ Kết nối OK — Sheet: **{info['title']}** / Tab: **{info['tab_title']}**"
                    )
                    st.write(f"Headers hiện có: `{info['headers']}`")
                    if info["missing_headers"]:
                        st.warning(f"Thiếu cột: `{info['missing_headers']}`")
                        st.session_state["sheet_create_header"] = (sheet_id.strip(), tab_name.strip())
                    else:
                        st.info("Đầy đủ 7 cột header A–G ✅")
                except sheets_client.SheetError as e:
                    st.error(f"❌ {e}")
                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")

    with col2:
        if st.button("💾 Lưu config", use_container_width=True):
            if not sheet_id.strip():
                st.error("Cần điền Sheet ID.")
            else:
                _save_config(sheet_id.strip(), tab_name.strip())
                st.success("Đã lưu config.")
                st.rerun()

    if "sheet_create_header" in st.session_state:
        sid, tab = st.session_state["sheet_create_header"]
        if st.button("➕ Tạo header tự động (A1:G1)"):
            try:
                sheets_client.create_header(creds_path, sid, tab)
                st.success("Đã tạo header.")
                del st.session_state["sheet_create_header"]
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

    if cfg:
        st.divider()
        st.subheader("3. Config hiện tại")
        c1, c2, c3 = st.columns(3)
        c1.write(f"**Sheet ID**: `{cfg.sheet_id[:20]}...`")
        c2.write(f"**Tab**: `{cfg.tab_name}`")
        c3.write(
            f"**Last synced**: "
            f"{cfg.last_synced_at.strftime('%Y-%m-%d %H:%M') if cfg.last_synced_at else '—'}"
        )
