"""ThreadPoolExecutor chạy batch 10 page/lần — Cấp 2 Cân bằng."""
import json
import logging
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from itertools import islice
from pathlib import Path
from typing import Iterable, TypeVar

from src.config import (
    BATCH_SIZE,
    GOOGLE_CREDENTIALS_PATH,
    MAX_BATCH_DELAY,
    MIN_BATCH_DELAY,
)
from src.database import SessionLocal, get_session
from src.models import Page, Post, PostLog, SheetsConfig
from src.services import fb_client, sheets_client
from src.services.poster import post_one_page


def _make_step_updater(post_id: int):
    """Tạo callback thread-safe để update Post.progress_step từ thread."""
    def update(step: str) -> None:
        db = SessionLocal()
        try:
            p = db.query(Post).filter(Post.id == post_id).first()
            if p:
                p.progress_step = step
                p.progress_updated_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass
        finally:
            db.close()
    return update

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _chunked(iterable: Iterable[T], n: int) -> list[list[T]]:
    it = iter(iterable)
    chunks: list[list[T]] = []
    while batch := list(islice(it, n)):
        chunks.append(batch)
    return chunks


def run_post_campaign(post_id: int, dry_run: bool = False) -> None:
    db = get_session()
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            logger.error("Post %s không tồn tại", post_id)
            return

        page_db_ids = json.loads(post.target_page_ids or "[]")
        pages = db.query(Page).filter(
            Page.id.in_(page_db_ids), Page.is_active == True  # noqa: E712
        ).all()

        if not pages:
            post.status = "failed"
            db.commit()
            logger.error("Post %s không có active page nào", post_id)
            return

        post.status = "running"
        post.progress_step = f"🚀 Khởi động — {len(pages)} page chia thành {(len(pages) + BATCH_SIZE - 1) // BATCH_SIZE} batch"
        post.progress_updated_at = datetime.utcnow()
        db.commit()

        batches = _chunked(pages, BATCH_SIZE)
        fb_post_ids_by_page: dict[str, str] = {}
        step_cb = _make_step_updater(post.id)

        for batch_idx, batch in enumerate(batches, start=1):
            step_cb(f"📦 Batch {batch_idx}/{len(batches)} — đang xử lý {len(batch)} page song song")

            log_ids: dict[int, int] = {}
            for page in batch:
                log = PostLog(
                    post_id=post.id,
                    page_id=page.id,
                    batch_index=batch_idx,
                    status="pending",
                )
                db.add(log)
                db.flush()
                log_ids[page.id] = log.id
            db.commit()

            with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
                futures = {
                    executor.submit(
                        post_one_page,
                        page.page_id,
                        page.access_token,
                        post.caption,
                        post.video_link,
                        post.comment_text,
                        post.shopee_link,
                        post.variant_mode,
                        dry_run,
                        page.name,
                        step_cb,
                        log_ids[page.id],
                    ): page
                    for page in batch
                }
                for future in as_completed(futures):
                    page = futures[future]
                    try:
                        result = future.result()
                        fb_post_ids_by_page[page.page_id] = result.fb_post_id
                    except fb_client.FbApiError as e:
                        log = db.query(PostLog).filter(PostLog.id == log_ids[page.id]).first()
                        if log:
                            log.error_message = str(e)
                            log.status = "failed"
                            db.commit()
                        if e.code in (190, 102):
                            page.token_expired = True
                            db.commit()
                    except Exception as e:
                        logger.exception("Lỗi không xác định khi đăng page %s", page.page_id)
                        log = db.query(PostLog).filter(PostLog.id == log_ids[page.id]).first()
                        if log:
                            log.error_message = f"{type(e).__name__}: {e}"
                            log.status = "failed"
                            db.commit()

            if batch_idx < len(batches):
                delay = random.uniform(MIN_BATCH_DELAY, MAX_BATCH_DELAY)
                step_cb(f"⏸️ Batch {batch_idx}/{len(batches)} xong — đợi {delay:.0f}s trước batch tiếp theo")
                logger.info("Post %s: chờ %.0fs trước batch tiếp theo", post_id, delay)
                time.sleep(delay)

        success_count = db.query(PostLog).filter(
            PostLog.post_id == post.id, PostLog.status == "success"
        ).count()
        total = len(pages)
        if success_count == total:
            post.status = "success"
            post.progress_step = f"✅ Hoàn tất — {success_count}/{total} page thành công"
        elif success_count == 0:
            post.status = "failed"
            post.progress_step = f"❌ Thất bại — 0/{total} page thành công"
        else:
            post.status = "partial"
            post.progress_step = f"⚠️ Một phần — {success_count}/{total} page thành công"
        post.progress_updated_at = datetime.utcnow()
        post.completed_at = datetime.utcnow()
        db.commit()

        if not dry_run and post.sheet_row_index and fb_post_ids_by_page:
            try:
                cfg = db.query(SheetsConfig).filter(
                    SheetsConfig.is_active == True  # noqa: E712
                ).first()
                if cfg:
                    sheets_client.mark_row_done(
                        Path(GOOGLE_CREDENTIALS_PATH),
                        cfg.sheet_id,
                        cfg.tab_name,
                        post.sheet_row_index,
                        fb_post_ids_by_page,
                    )
            except Exception:
                logger.exception("Update Sheet sau campaign %s thất bại", post_id)

    finally:
        db.close()


def run_in_background(post_id: int, dry_run: bool = False) -> threading.Thread:
    thread = threading.Thread(
        target=run_post_campaign,
        args=(post_id, dry_run),
        daemon=True,
        name=f"campaign-{post_id}",
    )
    thread.start()
    return thread
