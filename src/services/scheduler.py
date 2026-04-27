"""APScheduler background — chạy job đặt lịch trong-process."""
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from src.database import get_session
from src.models import Post

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _trigger_campaign(post_id: int) -> None:
    from src.services.batch_runner import run_post_campaign
    run_post_campaign(post_id)


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone="Asia/Ho_Chi_Minh")
        _scheduler.start()
        _restore_pending_jobs()
    return _scheduler


def _restore_pending_jobs() -> None:
    db = get_session()
    try:
        rows = db.query(Post).filter(
            Post.status == "pending",
            Post.scheduled_at.isnot(None),
        ).all()
        now = datetime.utcnow()
        for p in rows:
            if p.scheduled_at and p.scheduled_at > now:
                _scheduler.add_job(
                    _trigger_campaign,
                    "date",
                    run_date=p.scheduled_at,
                    args=[p.id],
                    id=f"post_{p.id}",
                    replace_existing=True,
                )
    finally:
        db.close()


def schedule_post(post_id: int, run_at: datetime) -> None:
    s = get_scheduler()
    s.add_job(
        _trigger_campaign,
        "date",
        run_date=run_at,
        args=[post_id],
        id=f"post_{post_id}",
        replace_existing=True,
    )


def cancel_scheduled(post_id: int) -> bool:
    s = get_scheduler()
    if s.get_job(f"post_{post_id}"):
        s.remove_job(f"post_{post_id}")
        return True
    return False
