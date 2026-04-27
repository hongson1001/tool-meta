"""Wrapper đọc/ghi Google Sheets."""
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

EXPECTED_HEADERS = [
    "video_link", "caption", "shopee_link", "comment_text",
    "used", "posted_at", "fb_post_ids",
]


class SheetError(Exception):
    pass


@dataclass
class SheetRow:
    row_index: int
    video_link: str
    caption: str
    shopee_link: str
    comment_text: str
    used: str
    posted_at: str
    fb_post_ids: str


def _client(credentials_path: Path) -> gspread.Client:
    if not Path(credentials_path).exists():
        raise SheetError(f"Không tìm thấy file credentials: {credentials_path}")
    creds = Credentials.from_service_account_file(str(credentials_path), scopes=SCOPES)
    return gspread.authorize(creds)


def open_worksheet(credentials_path: Path, sheet_id: str, tab_name: str):
    client = _client(credentials_path)
    try:
        sh = client.open_by_key(sheet_id)
    except gspread.exceptions.APIError as e:
        raise SheetError(f"Mở Sheet thất bại: {e}") from e
    try:
        return sh.worksheet(tab_name)
    except gspread.WorksheetNotFound as e:
        raise SheetError(f"Không thấy tab '{tab_name}' trong Sheet") from e


def verify_connection(credentials_path: Path, sheet_id: str, tab_name: str) -> dict:
    ws = open_worksheet(credentials_path, sheet_id, tab_name)
    headers = ws.row_values(1)
    missing = [h for h in EXPECTED_HEADERS if h not in headers]
    return {
        "title": ws.spreadsheet.title,
        "tab_title": ws.title,
        "headers": headers,
        "missing_headers": missing,
        "rows_count": ws.row_count,
        "ok": not missing,
    }


def fetch_pending_posts(credentials_path: Path, sheet_id: str, tab_name: str) -> list[SheetRow]:
    ws = open_worksheet(credentials_path, sheet_id, tab_name)
    records = ws.get_all_records()
    rows: list[SheetRow] = []
    for i, r in enumerate(records, start=2):
        used_val = str(r.get("used", "")).strip().upper()
        if used_val == "TRUE":
            continue
        rows.append(SheetRow(
            row_index=i,
            video_link=str(r.get("video_link", "")).strip(),
            caption=str(r.get("caption", "")).strip(),
            shopee_link=str(r.get("shopee_link", "")).strip(),
            comment_text=str(r.get("comment_text", "")).strip(),
            used=used_val,
            posted_at=str(r.get("posted_at", "")),
            fb_post_ids=str(r.get("fb_post_ids", "")),
        ))
    return rows


def mark_row_done(
    credentials_path: Path,
    sheet_id: str,
    tab_name: str,
    row_index: int,
    fb_post_ids_by_page: dict[str, str],
) -> None:
    ws = open_worksheet(credentials_path, sheet_id, tab_name)
    ws.update(
        range_name=f"E{row_index}:G{row_index}",
        values=[[
            "TRUE",
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            json.dumps(fb_post_ids_by_page, ensure_ascii=False),
        ]],
    )


def create_header(credentials_path: Path, sheet_id: str, tab_name: str) -> None:
    ws = open_worksheet(credentials_path, sheet_id, tab_name)
    ws.update(range_name="A1:G1", values=[EXPECTED_HEADERS])
