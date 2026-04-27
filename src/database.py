"""Khởi tạo SQLAlchemy engine + session."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import DB_PATH


class Base(DeclarativeBase):
    pass


engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    from src.models import account, page, post, post_log, sheets_config  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _migrate_columns()


def _migrate_columns() -> None:
    from sqlalchemy import text
    with engine.begin() as conn:
        for stmt in (
            "ALTER TABLE posts ADD COLUMN progress_step VARCHAR(255) DEFAULT ''",
            "ALTER TABLE posts ADD COLUMN progress_updated_at DATETIME",
            "ALTER TABLE pages ADD COLUMN account_id INTEGER",
        ):
            try:
                conn.execute(text(stmt))
            except Exception:
                pass


def get_session():
    return SessionLocal()
