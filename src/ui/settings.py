"""Tab cài đặt chung — config xem-only + backup/restore DB."""
import shutil
from datetime import datetime

import streamlit as st

from src.config import (
    BASE_DIR,
    BATCH_SIZE,
    DB_PATH,
    ENABLE_CONTENT_VARIANT,
    MAX_BATCH_DELAY,
    MAX_COMMENT_DELAY,
    MAX_PAGE_DELAY_IN_BATCH,
    MAX_POSTS_PER_PAGE_PER_DAY,
    MIN_BATCH_DELAY,
    MIN_COMMENT_DELAY,
    MIN_PAGE_DELAY_IN_BATCH,
)

BACKUP_DIR = BASE_DIR / "backups"


def render() -> None:
    st.header("⚙️ Cài Đặt")

    st.subheader("Batch posting (đọc từ `.env`)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Batch size", BATCH_SIZE)
    c2.metric("Min batch delay", f"{MIN_BATCH_DELAY}s")
    c3.metric("Max batch delay", f"{MAX_BATCH_DELAY}s")

    c4, c5, c6 = st.columns(3)
    c4.metric("Min page delay/batch", f"{MIN_PAGE_DELAY_IN_BATCH}s")
    c5.metric("Max page delay/batch", f"{MAX_PAGE_DELAY_IN_BATCH}s")
    c6.metric("Max posts/page/day", MAX_POSTS_PER_PAGE_PER_DAY)

    c7, c8, c9 = st.columns(3)
    c7.metric("Min comment delay", f"{MIN_COMMENT_DELAY}s")
    c8.metric("Max comment delay", f"{MAX_COMMENT_DELAY}s")
    c9.metric("Variant default", "ON" if ENABLE_CONTENT_VARIANT else "OFF")

    st.caption(
        "Sửa các giá trị trên trong file `.env` rồi restart tool "
        "(`streamlit run src/ui/app.py`)."
    )

    st.divider()
    st.subheader("Backup / Restore Database")
    st.write(f"**DB hiện tại**: `{DB_PATH}`")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    cb1, cb2 = st.columns(2)
    with cb1:
        if st.button("💾 Backup ngay", use_container_width=True):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            target = BACKUP_DIR / f"posts_{ts}.db"
            shutil.copy2(DB_PATH, target)
            st.success(f"Backup → `{target.name}`")
            st.rerun()

    with cb2:
        uploaded = st.file_uploader("Restore từ file `.db`", type=["db"])
        if uploaded and st.button("⚠️ Restore (overwrite DB hiện tại)"):
            with DB_PATH.open("wb") as f:
                f.write(uploaded.read())
            st.success("Restore xong. Restart tool để áp dụng.")

    backups = sorted(BACKUP_DIR.glob("*.db"), reverse=True)
    if backups:
        st.write(f"**Backups ({len(backups)} file):**")
        for b in backups[:10]:
            st.write(f"- `{b.name}` ({b.stat().st_size // 1024} KB)")
