"""Logic đăng 1 page (caption + 1 comment Shopee link)."""
import random
import time
from dataclasses import dataclass
from typing import Callable, Optional

from src.config import (
    MAX_COMMENT_DELAY,
    MAX_PAGE_DELAY_IN_BATCH,
    MIN_COMMENT_DELAY,
    MIN_PAGE_DELAY_IN_BATCH,
)
from src.services import fb_client
from src.services.variant import build_final_caption


@dataclass
class PostResult:
    fb_post_id: str
    fb_post_url: str
    applied_caption: str
    fb_comment_id: str | None
    comment_error: str | None = None


ProgressCallback = Optional[Callable[[str], None]]


def fb_post_url_from_id(fb_post_id: str) -> str:
    if "_" in fb_post_id:
        page_id, post_id = fb_post_id.split("_", 1)
        return f"https://facebook.com/{page_id}/posts/{post_id}"
    return f"https://facebook.com/{fb_post_id}"


def _update_log(log_id: int | None, **kwargs) -> None:
    """Cập nhật PostLog từ trong worker thread (mỗi thread mở session riêng)."""
    if not log_id:
        return
    from src.database import SessionLocal
    from src.models import PostLog
    db = SessionLocal()
    try:
        log = db.query(PostLog).filter(PostLog.id == log_id).first()
        if log:
            for k, v in kwargs.items():
                setattr(log, k, v)
            db.commit()
    except Exception:
        pass
    finally:
        db.close()


def post_one_page(
    page_id: str,
    page_token: str,
    base_caption: str,
    video_link: str,
    comment_text: str,
    shopee_link: str,
    variant_mode: str = "auto_variant",
    dry_run: bool = False,
    page_name: str = "",
    progress_cb: ProgressCallback = None,
    log_id: int | None = None,
) -> PostResult:
    label = page_name or page_id
    _update_log(log_id, status="queued")
    if progress_cb:
        progress_cb(f"⏳ [{label}] đợi vài giây trước khi đăng...")
    time.sleep(random.uniform(MIN_PAGE_DELAY_IN_BATCH, MAX_PAGE_DELAY_IN_BATCH))

    final_caption = build_final_caption(base_caption, video_link, variant_mode)

    if dry_run:
        if progress_cb:
            progress_cb(f"🧪 [{label}] Dry Run — bỏ qua FB API")
        fake_id = f"DRY_{page_id}_{random.randint(10000, 99999)}"
        _update_log(
            log_id,
            applied_caption=final_caption,
            fb_post_id=fake_id,
            fb_post_url=fb_post_url_from_id(fake_id),
            fb_comment_id="DRY_COMMENT",
            comment_posted=True,
            status="success",
        )
        return PostResult(
            fb_post_id=fake_id,
            fb_post_url=fb_post_url_from_id(fake_id),
            applied_caption=final_caption,
            fb_comment_id="DRY_COMMENT",
        )

    _update_log(log_id, status="posting", applied_caption=final_caption)
    if progress_cb:
        progress_cb(f"📝 [{label}] đang đăng bài...")
    fb_post_id = fb_client.post_to_page(page_id, page_token, final_caption)
    fb_post_url = fb_post_url_from_id(fb_post_id)
    _update_log(log_id, fb_post_id=fb_post_id, fb_post_url=fb_post_url)

    fb_comment_id = None
    comment_error = None
    final_comment = ""
    if comment_text:
        final_comment = comment_text.strip()
    if shopee_link:
        final_comment = (final_comment + "\n" + shopee_link.strip()).strip()

    if final_comment:
        delay = random.uniform(MIN_COMMENT_DELAY, MAX_COMMENT_DELAY)
        _update_log(log_id, status="waiting_comment")
        if progress_cb:
            progress_cb(f"⏸️ [{label}] đã đăng bài, đợi {delay:.0f}s trước khi comment...")
        time.sleep(delay)
        _update_log(log_id, status="commenting")
        if progress_cb:
            progress_cb(f"💬 [{label}] đang đăng comment...")
        try:
            fb_comment_id = fb_client.post_comment(fb_post_id, page_token, final_comment)
            _update_log(
                log_id,
                fb_comment_id=fb_comment_id,
                comment_posted=True,
                status="success",
            )
        except fb_client.FbApiError as e:
            comment_error = f"Comment failed: {e}"
            _update_log(
                log_id,
                error_message=comment_error,
                comment_posted=False,
                status="success",
            )
    else:
        _update_log(log_id, status="success")

    if progress_cb:
        progress_cb(f"✅ [{label}] hoàn tất")

    return PostResult(
        fb_post_id=fb_post_id,
        fb_post_url=fb_post_url,
        applied_caption=final_caption,
        fb_comment_id=fb_comment_id,
        comment_error=comment_error,
    )
