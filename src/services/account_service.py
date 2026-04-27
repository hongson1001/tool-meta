"""Logic cao cấp cho tài khoản FB: OAuth, exchange token, lưu DB, sync pages."""
from datetime import datetime
from dataclasses import dataclass

import requests

from src.config import (
    FB_API_VERSION,
    FB_APP_ID,
    FB_APP_SECRET,
    OAUTH_BACKEND_URL,
)
from src.database import get_session
from src.models import Account, Page
from src.services import fb_client, oauth_local


SCOPES = [
    "pages_show_list",
    "pages_manage_posts",
    "pages_read_engagement",
    "pages_manage_engagement",
]


@dataclass
class AuthorizeResult:
    account_id: int
    name: str
    fb_user_id: str
    is_long_lived: bool
    pages_count: int


class AccountAuthError(Exception):
    pass


def _exchange_via_backend(code: str, redirect_uri: str) -> dict:
    """Gọi Cloudflare Worker backend exchange code → long-lived token."""
    res = requests.post(
        OAUTH_BACKEND_URL,
        json={"code": code, "redirect_uri": redirect_uri},
        timeout=30,
    )
    res.raise_for_status()
    data = res.json()
    if "error" in data:
        raise AccountAuthError(f"Backend exchange thất bại: {data['error']}")
    return data


def _exchange_direct(code: str, redirect_uri: str) -> dict:
    """Exchange code → token trực tiếp (cần FB_APP_SECRET trong .env)."""
    if not FB_APP_SECRET:
        raise AccountAuthError(
            "Thiếu FB_APP_SECRET trong .env. Hãy điền App Secret từ Dashboard FB → Settings → Basic, "
            "hoặc cấu hình OAUTH_BACKEND_URL để dùng backend Cloudflare Worker."
        )

    short_token = fb_client.exchange_code_for_token(code, FB_APP_ID, FB_APP_SECRET, redirect_uri)
    is_long_lived = False
    long_token = short_token
    try:
        long_token = fb_client.convert_to_long_lived(short_token, FB_APP_ID, FB_APP_SECRET)
        is_long_lived = True
    except Exception:
        pass

    return {"access_token": long_token, "is_long_lived": is_long_lived}


def authorize_new_account() -> AuthorizeResult:
    """Toàn bộ flow connect 1 tài khoản FB mới (hoặc re-authorize tài khoản cũ).

    1. Mở browser OAuth → user cấp quyền
    2. Exchange code → long-lived User Token
    3. Lấy User ID + name qua /me
    4. Save Account vào DB (upsert theo fb_user_id)
    5. Fetch /me/accounts → save Pages, link account_id
    """
    result = oauth_local.start_oauth_flow(FB_APP_ID, SCOPES, api_version=FB_API_VERSION)
    code = result["code"]
    redirect_uri = result["redirect_uri"]

    if OAUTH_BACKEND_URL:
        token_data = _exchange_via_backend(code, redirect_uri)
        user_token = token_data["access_token"]
        is_long_lived = bool(token_data.get("is_long_lived", True))
    else:
        token_data = _exchange_direct(code, redirect_uri)
        user_token = token_data["access_token"]
        is_long_lived = bool(token_data.get("is_long_lived", False))

    me = fb_client.get_me(user_token)
    fb_user_id = me["id"]
    name = me.get("name", fb_user_id)

    with get_session() as db:
        existing = db.query(Account).filter(Account.fb_user_id == fb_user_id).first()
        if existing:
            existing.user_token = user_token
            existing.name = name
            existing.is_long_lived = is_long_lived
            existing.token_expired = False
            existing.is_active = True
            existing.last_authorized_at = datetime.utcnow()
            account_id = existing.id
        else:
            new_acc = Account(
                fb_user_id=fb_user_id,
                name=name,
                user_token=user_token,
                is_long_lived=is_long_lived,
                last_authorized_at=datetime.utcnow(),
            )
            db.add(new_acc)
            db.flush()
            account_id = new_acc.id
        db.commit()

    pages_count = sync_pages_for_account(account_id)

    return AuthorizeResult(
        account_id=account_id,
        name=name,
        fb_user_id=fb_user_id,
        is_long_lived=is_long_lived,
        pages_count=pages_count,
    )


def sync_pages_for_account(account_id: int) -> int:
    """Gọi /me/accounts với User Token của account, upsert Pages vào DB.

    Trả về số page đã sync. Đánh dấu token_expired nếu User Token invalid.
    """
    with get_session() as db:
        acc = db.query(Account).filter(Account.id == account_id).first()
        if not acc:
            return 0

        try:
            pages = fb_client.list_user_pages(acc.user_token)
        except fb_client.FbApiError as e:
            if e.code in (190, 102):
                acc.token_expired = True
                db.commit()
            raise

        for p in pages:
            existing = db.query(Page).filter(Page.page_id == p.page_id).first()
            if existing:
                existing.name = p.name
                existing.access_token = p.access_token
                existing.account_id = account_id
                existing.owner_account_label = acc.name
                existing.token_expired = False
                existing.is_active = True
            else:
                db.add(Page(
                    page_id=p.page_id,
                    name=p.name,
                    access_token=p.access_token,
                    account_id=account_id,
                    owner_account_label=acc.name,
                    is_active=True,
                ))
        db.commit()
        return len(pages)


def remove_account(account_id: int) -> None:
    """Xóa tài khoản và tất cả Pages của tài khoản đó khỏi DB."""
    with get_session() as db:
        db.query(Page).filter(Page.account_id == account_id).delete()
        db.query(Account).filter(Account.id == account_id).delete()
        db.commit()
