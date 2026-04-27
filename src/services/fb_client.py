"""Wrapper gọi Facebook Graph API."""
from dataclasses import dataclass

import requests

from src.config import FB_API_BASE


class FbApiError(Exception):
    def __init__(self, code: int | None, message: str, subcode: int | None = None):
        self.code = code
        self.subcode = subcode
        self.message = message
        super().__init__(f"FB API error [{code}/{subcode}]: {message}")


@dataclass
class PageInfo:
    page_id: str
    name: str
    access_token: str


def _request(method: str, path: str, **kwargs) -> dict:
    url = f"{FB_API_BASE}/{path.lstrip('/')}"
    res = requests.request(method, url, timeout=30, **kwargs)
    data = res.json() if res.content else {}
    if not res.ok or "error" in data:
        err = data.get("error", {})
        raise FbApiError(
            code=err.get("code"),
            subcode=err.get("error_subcode"),
            message=err.get("message", res.text),
        )
    return data


def verify_page_token(page_id: str, access_token: str) -> dict:
    return _request(
        "GET",
        f"{page_id}",
        params={"fields": "id,name,category", "access_token": access_token},
    )


def list_user_pages(user_token: str) -> list[PageInfo]:
    data = _request(
        "GET",
        "me/accounts",
        params={"fields": "id,name,access_token", "access_token": user_token, "limit": 200},
    )
    return [
        PageInfo(page_id=p["id"], name=p["name"], access_token=p["access_token"])
        for p in data.get("data", [])
    ]


def post_to_page(page_id: str, access_token: str, message: str) -> str:
    data = _request(
        "POST",
        f"{page_id}/feed",
        data={
            "message": message,
            "access_token": access_token,
            "published": "true",
            "privacy": '{"value":"EVERYONE"}',
        },
    )
    return data["id"]


def post_comment(fb_post_id: str, access_token: str, message: str) -> str:
    data = _request(
        "POST",
        f"{fb_post_id}/comments",
        data={"message": message, "access_token": access_token},
    )
    return data["id"]


def exchange_code_for_token(code: str, app_id: str, app_secret: str, redirect_uri: str) -> str:
    """Đổi authorization code lấy User Access Token (short-lived ~1h)."""
    data = _request(
        "GET",
        "oauth/access_token",
        params={
            "client_id": app_id,
            "client_secret": app_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        },
    )
    return data["access_token"]


def convert_to_long_lived(short_token: str, app_id: str, app_secret: str) -> str:
    """Convert short-lived User Token (1h) → long-lived (60 ngày). Page Token derived sẽ vĩnh viễn."""
    data = _request(
        "GET",
        "oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_token,
        },
    )
    return data["access_token"]


def get_me(access_token: str) -> dict:
    """Lấy thông tin User của token: id + name."""
    return _request(
        "GET",
        "me",
        params={"fields": "id,name", "access_token": access_token},
    )
