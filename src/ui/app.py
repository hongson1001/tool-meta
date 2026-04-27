"""Streamlit entry point."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from streamlit_option_menu import option_menu

from src.database import init_db
from src.services.scheduler import get_scheduler
from src.ui import (
    accounts_manager,
    history,
    page_manager,
    post_creator,
    scheduler_view,
    settings,
    sheets_config,
)

st.set_page_config(page_title="FB Auto Post Tool", page_icon="📣", layout="wide")

init_db()
get_scheduler()

with st.sidebar:
    st.title("📣 FB Auto Post")
    selected = option_menu(
        menu_title=None,
        options=["Tài khoản FB", "Fanpages", "Google Sheet", "Tạo Bài", "Lịch Đăng", "Lịch Sử", "Cài Đặt"],
        icons=["person-badge", "people", "table", "pencil-square", "clock", "clock-history", "gear"],
        default_index=0,
    )

if selected == "Tài khoản FB":
    accounts_manager.render()
elif selected == "Fanpages":
    page_manager.render()
elif selected == "Google Sheet":
    sheets_config.render()
elif selected == "Tạo Bài":
    post_creator.render()
elif selected == "Lịch Đăng":
    scheduler_view.render()
elif selected == "Lịch Sử":
    history.render()
elif selected == "Cài Đặt":
    settings.render()
