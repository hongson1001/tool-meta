"""Load config từ file .env."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

FB_APP_ID = os.getenv("FB_APP_ID", "")
FB_APP_SECRET = os.getenv("FB_APP_SECRET", "")
FB_API_VERSION = os.getenv("FB_API_VERSION", "v19.0")
FB_API_BASE = f"https://graph.facebook.com/{FB_API_VERSION}"

# OAuth backend (Cloudflare Worker) — chỉ dùng ở production khi không muốn lưu App Secret trong tool
OAUTH_BACKEND_URL = os.getenv("OAUTH_BACKEND_URL", "").strip()
OAUTH_REDIRECT_PORT = int(os.getenv("OAUTH_REDIRECT_PORT", "8765"))

GOOGLE_CREDENTIALS_PATH = BASE_DIR / os.getenv("GOOGLE_CREDENTIALS_PATH", "data/credentials.json")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_SHEET_TAB = os.getenv("GOOGLE_SHEET_TAB", "posts")

DB_PATH = BASE_DIR / os.getenv("DB_PATH", "data/posts.db")
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "data/uploads")
LOG_PATH = BASE_DIR / os.getenv("LOG_PATH", "logs/app.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))
MIN_BATCH_DELAY = int(os.getenv("MIN_BATCH_DELAY", 180))
MAX_BATCH_DELAY = int(os.getenv("MAX_BATCH_DELAY", 300))
MIN_PAGE_DELAY_IN_BATCH = int(os.getenv("MIN_PAGE_DELAY_IN_BATCH", 2))
MAX_PAGE_DELAY_IN_BATCH = int(os.getenv("MAX_PAGE_DELAY_IN_BATCH", 8))

MIN_COMMENT_DELAY = int(os.getenv("MIN_COMMENT_DELAY", 15))
MAX_COMMENT_DELAY = int(os.getenv("MAX_COMMENT_DELAY", 30))
COMMENTS_PER_POST = int(os.getenv("COMMENTS_PER_POST", 1))

MAX_POSTS_PER_PAGE_PER_DAY = int(os.getenv("MAX_POSTS_PER_PAGE_PER_DAY", 20))
ENABLE_CONTENT_VARIANT = os.getenv("ENABLE_CONTENT_VARIANT", "true").lower() == "true"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
