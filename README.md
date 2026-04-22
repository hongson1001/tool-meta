# FB Auto Post Tool

Tool desktop tự động đăng bài + comment affiliate lên nhiều Facebook Fanpage thuộc nhiều tài khoản cá nhân, lấy nội dung từ Google Sheets.

## Mô hình sử dụng

```text
N tài khoản FB cá nhân (~10)
  ├─ Tài khoản 1 → quản lý ~5 page
  ├─ Tài khoản 2 → quản lý ~5 page
  └─ ... → Tổng: ~50+ page
              ↓
        1 Sheet row = 1 bài đăng (caption + video + Shopee link)
              ↓
  Tool chia 5 batch × 10 page, delay 3–5 phút giữa batch
              ↓
  Mỗi page: đăng bài + 1 comment gắn Shopee link
              ↓
  Update Sheet: đánh dấu "Đã dùng" + ghi FB post ID
```

## Tính năng chính

- ✅ Đăng bài (caption + link video YouTube/TikTok/IG) lên **50+ Fanpage** thuộc nhiều tài khoản cá nhân
- ✅ Chế độ **Cấp 2 — Cân bằng**: 5 batch × 10 page song song, delay 3–5 phút giữa batch, ~20 phút/đợt
- ✅ **Nguồn nội dung từ Google Sheets** (caption, link video, link Shopee, text comment)
- ✅ **1 comment / bài** tự động gắn link sản phẩm Shopee/affiliate
- ✅ Tự động **update Sheet** sau khi đăng: đánh dấu đã dùng + lưu FB post ID
- ✅ Biến thể nội dung nhẹ (emoji/câu mở-kết) để tránh FB flag duplicate — có toggle "đăng y hệt"
- ✅ Đặt lịch đăng bài theo giờ / ngày / tuần
- ✅ Dashboard xem lịch sử, thống kê, link video gốc + link FB post
- ✅ Build thành file `.exe` dùng trên Windows (không cần cài Python)

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.11+ |
| UI | Streamlit |
| Database | SQLite (SQLAlchemy ORM) |
| HTTP Client | Requests |
| Nguồn nội dung | Google Sheets API (gspread) |
| Lập lịch | APScheduler |
| Chạy song song | ThreadPoolExecutor (batch 10 page) |
| Đóng gói | PyInstaller |

## Bắt đầu nhanh

```bash
# 1. Kích hoạt venv
venv\Scripts\activate

# 2. Cài thư viện
pip install -r requirements.txt

# 3. Copy .env.example thành .env và điền thông tin
copy .env.example .env

# 4. Chạy tool
streamlit run src/ui/app.py
```

## Mục lục

1. [Hướng dẫn cài đặt môi trường](#1-hướng-dẫn-cài-đặt-môi-trường) (gồm Facebook App + Google Cloud Service Account)
2. [Danh sách thư viện cần cài](#2-danh-sách-thư-viện-cần-cài)
3. [Setup Project Python](#3-setup-project-python)
4. [Các chức năng cần làm](#4-các-chức-năng-cần-làm)
5. [Lộ trình phát triển](#5-lộ-trình-phát-triển)
6. [Lưu ý quan trọng & Bảo mật](#6-lưu-ý-quan-trọng--bảo-mật)

---

# 1. HƯỚNG DẪN CÀI ĐẶT MÔI TRƯỜNG

## 1.1: Cài Python

**Download**: https://www.python.org/downloads/

- Chọn phiên bản **Python 3.11** hoặc **3.12** (khuyên dùng 3.11, ổn định nhất)
- ⚠️ **BẮT BUỘC tick ô "Add Python to PATH"** ở màn hình đầu tiên khi cài
- Tick "Install for all users"
- Nhấn **Install Now**

### Kiểm tra đã cài thành công

Mở **PowerShell** hoặc **CMD** mới (phải mở lại sau khi cài), gõ:

```bash
python --version
pip --version
```

Kết quả phải hiện:

```
Python 3.11.x
pip 24.x.x
```

Nếu báo `python is not recognized` → bạn chưa tick "Add to PATH" → cài lại.

## 1.2: Cài VS Code (khuyến nghị)

**Download**: https://code.visualstudio.com/

### Extensions cần cài

| Extension | Nhà phát hành | Công dụng |
|---|---|---|
| Python | Microsoft | Hỗ trợ ngôn ngữ Python |
| Pylance | Microsoft | Autocomplete, type checking |
| SQLite Viewer | Florian Klampfer | Xem file `.db` trực tiếp trong VS Code |
| Better Comments | Aaron Bond | Highlight comment quan trọng |

## 1.3: Cài Git (tùy chọn)

**Download**: https://git-scm.com/download/win

- Mặc định Next → Next là được
- Dùng để backup code và version control

## 1.4: Tạo Facebook App

### 1.4.1: Tạo App

1. Truy cập: https://developers.facebook.com/apps
2. Nhấn **Create App**
3. Chọn loại: **Business** → Next
4. Điền thông tin:
   - App name: `FB Auto Post Tool`
   - App contact email: email của bạn
5. Nhấn **Create app**

### 1.4.2: Lấy App ID và App Secret

Vào **Settings → Basic**:

- **App ID**: copy lại
- **App Secret**: nhấn **Show** để xem và copy

## 1.5: Xin quyền (Permissions)

Vào **App Review → Permissions and Features**, request các quyền sau:

| Permission | Mục đích |
|---|---|
| `pages_show_list` | Liệt kê danh sách page bạn quản lý |
| `pages_manage_posts` | Đăng bài lên page |
| `pages_read_engagement` | Đọc comment, like |
| `pages_manage_engagement` | Comment, like bài viết |

⚠️ **Lưu ý**: Với app ở chế độ **Development**, bạn (admin) đã test được luôn mà không cần App Review. Chỉ cần submit App Review khi muốn đưa tool cho người khác dùng.

## 1.6: Lấy Page Access Token

### 1.6.1: Lấy User Access Token

1. Truy cập: https://developers.facebook.com/tools/explorer/
2. Chọn **App** của bạn ở dropdown góc phải
3. Nhấn **Generate Access Token**
4. Tick các permission ở Bước 1.5
5. Copy **User Access Token** (token này ngắn hạn, ~1 giờ)

### 1.6.2: Lấy Page Access Token (token chính sẽ dùng)

Trong Graph API Explorer, gọi:

```
GET /me/accounts
```

Response sẽ có dạng:

```json
{
  "data": [
    {
      "access_token": "EAAxxx...",
      "category": "...",
      "name": "Tên page",
      "id": "123456789"
    }
  ]
}
```

**Page Access Token** là token dùng để đăng bài, comment. Với page mà bạn là admin, token này **không hết hạn**.

### 1.6.3: Convert sang Long-lived Token (khuyến nghị)

Để token bền hơn, convert bằng URL:

```
GET https://graph.facebook.com/v19.0/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id={APP_ID}&
  client_secret={APP_SECRET}&
  fb_exchange_token={SHORT_LIVED_TOKEN}
```

## 1.7: Setup Google Cloud + Google Sheets API

Nội dung bài đăng (caption, video link, Shopee link, comment) được quản lý trong **Google Sheets**. Tool đọc Sheet khi đăng và update trạng thái sau khi đăng thành công.

### 1.7.1: Tạo Google Cloud Project

1. Truy cập: <https://console.cloud.google.com/>
2. Tạo **New Project** → tên: `FB Auto Post Tool`
3. Chọn project vừa tạo

### 1.7.2: Bật Google Sheets API + Google Drive API

1. Vào **APIs & Services → Library**
2. Tìm và bật 2 API:
   - **Google Sheets API**
   - **Google Drive API** (cần để share Sheet)

### 1.7.3: Tạo Service Account

1. **APIs & Services → Credentials** → **Create Credentials → Service Account**
2. Điền thông tin:
   - Service account name: `fb-auto-post-bot`
   - Role: để trống (không cần quyền GCP)
3. Nhấn **Done**

### 1.7.4: Tải `credentials.json`

1. Vào Service Account vừa tạo → tab **Keys**
2. **Add Key → Create new key → JSON**
3. File JSON tự động download → đổi tên thành `credentials.json`
4. Copy vào thư mục `data/` của project (xem mục 3.2)

⚠️ **TUYỆT ĐỐI không commit file này lên Git**. Đã có trong `.gitignore`.

### 1.7.5: Chuẩn bị Google Sheet

1. Tạo Sheet mới: <https://sheets.new>
2. Đặt tên (vd: `FB Content Queue`)
3. Tab đầu tiên đặt tên `posts`, tạo header theo cấu trúc sau:

| Cột | Header | Mô tả | Ví dụ |
|---|---|---|---|
| A | `video_link` | Link video (YouTube/TikTok/IG) | `https://youtu.be/abc123` |
| B | `caption` | Nội dung bài đăng trên FB | `Chị em xem review son này nè 😍` |
| C | `shopee_link` | Link sản phẩm Shopee/affiliate | `https://s.shopee.vn/xyz` |
| D | `comment_text` | Text comment tự động (sẽ đính kèm `shopee_link`) | `Link mua tại đây nha chị em` |
| E | `used` | Đã đăng chưa (tool auto-update) | `FALSE` / `TRUE` |
| F | `posted_at` | Ngày giờ đăng (tool auto-fill) | `2026-04-22 14:30` |
| G | `fb_post_ids` | JSON các FB post ID đã đăng (tool auto-fill) | `{"page_123": "123_456"}` |

### 1.7.6: Share Sheet cho Service Account

1. Mở `credentials.json` bằng notepad → tìm field `client_email`, copy giá trị (dạng `fb-auto-post-bot@xxx.iam.gserviceaccount.com`)
2. Trong Google Sheet → nhấn **Share** (góc phải)
3. Paste email service account → chọn quyền **Editor** → **Send**

### 1.7.7: Lấy Sheet ID

Trong URL Sheet có dạng: `https://docs.google.com/spreadsheets/d/`**`SHEET_ID_HERE`**`/edit`

Copy phần `SHEET_ID_HERE` để điền vào file `.env` (mục 3.3).

## Checklist Setup

- [ ] Cài Python 3.11+ và tick "Add to PATH"
- [ ] `python --version` chạy được ở terminal mới
- [ ] Cài VS Code + extension Python + SQLite Viewer
- [ ] Tạo Facebook App type Business
- [ ] Có **App ID** và **App Secret**
- [ ] Lấy được **User Access Token** từ Graph API Explorer
- [ ] Gọi `/me/accounts` lấy được **Page Access Token** cho từng page
- [ ] (Tùy) Convert sang Long-lived Token
- [ ] Tạo Google Cloud Project + bật Sheets API & Drive API
- [ ] Tạo Service Account + tải `credentials.json`
- [ ] Tạo Sheet với đúng 7 cột (A–G) + share cho service account email
- [ ] Lấy **Sheet ID** để điền `.env`

---

# 2. DANH SÁCH THƯ VIỆN CẦN CÀI

## 2.1: Thư viện có sẵn trong Python (không cần cài)

| Thư viện | Công dụng |
|---|---|
| `sqlite3` | Kết nối SQLite database |
| `os`, `sys` | Thao tác hệ điều hành, đường dẫn |
| `json` | Đọc/ghi file JSON |
| `datetime` | Xử lý thời gian |
| `random` | Random delay giữa comment |
| `time` | Sleep, timer |
| `logging` | Ghi log ra file |
| `threading` | Chạy đa luồng |
| `pathlib` | Thao tác đường dẫn file/folder hiện đại |

## 2.2: Thư viện cần cài qua pip

### Core — HTTP & Config

| Thư viện | Phiên bản | Công dụng |
|---|---|---|
| `requests` | 2.31.0 | Gọi HTTP tới Facebook Graph API |
| `python-dotenv` | 1.0.0 | Đọc file `.env` chứa config |

### Google Sheets Integration

| Thư viện | Phiên bản | Công dụng |
|---|---|---|
| `gspread` | 6.0.0 | Client đọc/ghi Google Sheets |
| `google-auth` | 2.28.0 | Auth Service Account |
| `google-auth-oauthlib` | 1.2.0 | OAuth flow (nếu mở rộng sau) |

### UI — Streamlit

| Thư viện | Phiên bản | Công dụng |
|---|---|---|
| `streamlit` | 1.32.0 | Tạo UI web local (không cần HTML/CSS) |
| `streamlit-option-menu` | 0.3.12 | Menu sidebar đẹp hơn |
| `streamlit-extras` | 0.4.0 | Các component mở rộng |

### Xử lý ảnh

| Thư viện | Phiên bản | Công dụng |
|---|---|---|
| `pillow` | 10.2.0 | Đọc, resize, nén ảnh trước khi upload |

### Database

| Thư viện | Phiên bản | Công dụng |
|---|---|---|
| `sqlalchemy` | 2.0.25 | ORM làm việc với SQLite dễ hơn |
| `alembic` | 1.13.1 | Migration DB khi đổi schema (tùy chọn) |

### Đặt lịch

| Thư viện | Phiên bản | Công dụng |
|---|---|---|
| `apscheduler` | 3.10.4 | Chạy task theo lịch / cron |

### Hiển thị dữ liệu

| Thư viện | Phiên bản | Công dụng |
|---|---|---|
| `pandas` | 2.2.0 | Hiển thị bảng log, thống kê |
| `plotly` | 5.19.0 | Biểu đồ dashboard |

### Build `.exe`

| Thư viện | Phiên bản | Công dụng |
|---|---|---|
| `pyinstaller` | 6.4.0 | Build project thành file `.exe` |

## 2.3: File `requirements.txt`

Copy nội dung sau vào file `requirements.txt` ở root project:

```txt
# Core
requests==2.31.0
python-dotenv==1.0.0

# Google Sheets
gspread==6.0.0
google-auth==2.28.0
google-auth-oauthlib==1.2.0

# UI
streamlit==1.32.0
streamlit-option-menu==0.3.12
streamlit-extras==0.4.0

# Image processing
pillow==10.2.0

# Database
sqlalchemy==2.0.25
alembic==1.13.1

# Scheduler
apscheduler==3.10.4

# Data display
pandas==2.2.0
plotly==5.19.0

# Build
pyinstaller==6.4.0
```

## 2.4: Cài đặt

Sau khi kích hoạt `venv`, chạy:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

⏳ Quá trình cài mất **3–5 phút** tùy tốc độ mạng.

## 2.5: Kiểm tra đã cài đầy đủ

```bash
pip list
```

Hoặc test nhanh:

```bash
python -c "import requests, streamlit, sqlalchemy, PIL, apscheduler, gspread; print('OK')"
```

→ In ra `OK` là đầy đủ.

---

# 3. SETUP PROJECT PYTHON

## 3.1: Tạo cấu trúc thư mục

### Tạo project root

Mở **PowerShell**, gõ:

```bash
cd D:\Sơn\Sơn\private
mkdir fb-auto-post
cd fb-auto-post
```

### Tạo virtual environment

**Virtual environment là gì?** Là "hộp cách ly" cho thư viện Python của project, tránh xung đột với các project khác trên máy.

```bash
python -m venv venv
```

→ Sẽ tạo thư mục `venv/` chứa Python runtime riêng cho project.

### Kích hoạt venv

**PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

Nếu báo lỗi *"running scripts is disabled"*, chạy lệnh này 1 lần:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**CMD:**
```cmd
venv\Scripts\activate.bat
```

**Git Bash:**
```bash
source venv/Scripts/activate
```

→ Khi kích hoạt thành công, đầu dòng lệnh sẽ có `(venv)`.

### Cài thư viện

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 3.2: Cấu trúc thư mục đầy đủ

```text
fb-auto-post/
├── venv/                          # Môi trường ảo (KHÔNG commit)
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point khi chạy .exe
│   ├── config.py                  # Load biến từ .env
│   ├── database.py                # Kết nối DB + khởi tạo SQLAlchemy
│   ├── models/
│   │   ├── __init__.py
│   │   ├── page.py                # Model Fanpage
│   │   ├── post.py                # Model bài đăng (1 row Sheet = 1 post)
│   │   ├── post_log.py            # Model log (per page)
│   │   └── sheets_config.py       # Model config Google Sheets
│   ├── services/
│   │   ├── __init__.py
│   │   ├── fb_client.py           # Wrapper gọi Graph API
│   │   ├── sheets_client.py       # Wrapper đọc/ghi Google Sheets
│   │   ├── poster.py              # Logic đăng bài + 1 comment
│   │   ├── batch_runner.py        # ThreadPoolExecutor chạy 10 page/batch
│   │   ├── variant.py             # Biến thể nội dung (emoji/câu mở-kết)
│   │   ├── scheduler.py           # APScheduler background
│   │   └── image_utils.py         # Resize, nén ảnh (nếu cần)
│   └── ui/
│       ├── __init__.py
│       ├── app.py                 # Streamlit entry point
│       ├── page_manager.py        # Tab quản lý fanpage
│       ├── post_creator.py        # Tab tạo bài từ Sheet
│       ├── sheets_config.py       # Tab config Google Sheets
│       ├── scheduler_view.py      # Tab lịch đăng
│       ├── history.py             # Tab lịch sử
│       └── settings.py            # Tab cài đặt
├── data/
│   ├── posts.db                   # SQLite DB (tự tạo khi chạy lần đầu)
│   ├── credentials.json           # Google Service Account key (KHÔNG commit)
│   └── uploads/                   # Ảnh thumbnail (nếu có)
├── logs/
│   └── app.log                    # File log
├── .env                           # Config (KHÔNG commit)
├── .env.example                   # Template cho .env
├── .gitignore
├── requirements.txt
└── README.md
```

## 3.3: Tạo các file config

### File `.env.example`

```env
# Facebook App
FB_APP_ID=123456789012345
FB_APP_SECRET=abc123def456ghi789
FB_API_VERSION=v19.0

# Google Sheets
GOOGLE_CREDENTIALS_PATH=data/credentials.json
GOOGLE_SHEET_ID=your-sheet-id-here
GOOGLE_SHEET_TAB=posts

# Database
DB_PATH=data/posts.db

# Uploads
UPLOAD_DIR=data/uploads
MAX_UPLOAD_SIZE_MB=10

# Logging
LOG_PATH=logs/app.log
LOG_LEVEL=INFO

# Batch posting (Cấp 2 — Cân bằng)
BATCH_SIZE=10
MIN_BATCH_DELAY=180
MAX_BATCH_DELAY=300

# Delay trong 1 batch (giây giữa các page trong 1 batch)
MIN_PAGE_DELAY_IN_BATCH=2
MAX_PAGE_DELAY_IN_BATCH=8

# Delay comment sau khi post (giây)
MIN_COMMENT_DELAY=15
MAX_COMMENT_DELAY=30

# Giới hạn an toàn
MAX_POSTS_PER_PAGE_PER_DAY=20
COMMENTS_PER_POST=1

# Biến thể nội dung (mặc định bật để tránh flag duplicate)
ENABLE_CONTENT_VARIANT=true
```

Sau đó copy thành `.env` và điền thông tin thật:

```bash
copy .env.example .env
```

### File `.gitignore`

```gitignore
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/

# Environment
.env

# Secrets (TUYỆT ĐỐI KHÔNG COMMIT)
data/credentials.json
*credentials*.json
*service-account*.json

# Database & user data
data/posts.db
data/posts.db-journal
data/uploads/

# Logs
logs/

# Build artifacts
dist/
build/
*.spec

# IDE
.vscode/
.idea/
*.swp

# OS
Thumbs.db
.DS_Store
```

### File `src/main.py` (skeleton)

```python
"""Entry point khi chạy tool."""
import subprocess
import sys
import webbrowser
from pathlib import Path

def main():
    ui_path = Path(__file__).parent / "ui" / "app.py"
    webbrowser.open("http://localhost:8501")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(ui_path),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ])

if __name__ == "__main__":
    main()
```

### File `src/config.py` (skeleton)

```python
"""Load config từ file .env."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

# Facebook
FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
FB_API_VERSION = os.getenv("FB_API_VERSION", "v19.0")
FB_API_BASE = f"https://graph.facebook.com/{FB_API_VERSION}"

# Google Sheets
GOOGLE_CREDENTIALS_PATH = BASE_DIR / os.getenv("GOOGLE_CREDENTIALS_PATH", "data/credentials.json")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_SHEET_TAB = os.getenv("GOOGLE_SHEET_TAB", "posts")

# Paths
DB_PATH = BASE_DIR / os.getenv("DB_PATH", "data/posts.db")
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "data/uploads")
LOG_PATH = BASE_DIR / os.getenv("LOG_PATH", "logs/app.log")

# Batch posting (Cấp 2 — Cân bằng)
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))
MIN_BATCH_DELAY = int(os.getenv("MIN_BATCH_DELAY", 180))
MAX_BATCH_DELAY = int(os.getenv("MAX_BATCH_DELAY", 300))
MIN_PAGE_DELAY_IN_BATCH = int(os.getenv("MIN_PAGE_DELAY_IN_BATCH", 2))
MAX_PAGE_DELAY_IN_BATCH = int(os.getenv("MAX_PAGE_DELAY_IN_BATCH", 8))

# Comment
MIN_COMMENT_DELAY = int(os.getenv("MIN_COMMENT_DELAY", 15))
MAX_COMMENT_DELAY = int(os.getenv("MAX_COMMENT_DELAY", 30))
COMMENTS_PER_POST = int(os.getenv("COMMENTS_PER_POST", 1))

# Safety
MAX_POSTS_PER_PAGE_PER_DAY = int(os.getenv("MAX_POSTS_PER_PAGE_PER_DAY", 20))
ENABLE_CONTENT_VARIANT = os.getenv("ENABLE_CONTENT_VARIANT", "true").lower() == "true"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
```

## 3.4: Thiết kế Database (SQLite)

### Bảng `pages` — Lưu Fanpage quản lý

| Cột | Kiểu | Mô tả |
|---|---|---|
| id | INTEGER PK | ID tự tăng |
| page_id | TEXT UNIQUE | ID Fanpage từ FB |
| name | TEXT | Tên page |
| access_token | TEXT | Page Access Token |
| is_active | BOOLEAN | Có đang dùng không |
| created_at | DATETIME | Ngày thêm |
| updated_at | DATETIME | Ngày cập nhật cuối |

### Bảng `posts` — Lưu bài đăng (1 row Sheet = 1 post)

| Cột | Kiểu | Mô tả |
|---|---|---|
| id | INTEGER PK | |
| sheet_row_index | INTEGER | Chỉ số dòng trong Sheet (để update lại) |
| caption | TEXT | Caption bài đăng (copy từ Sheet cột B) |
| video_link | TEXT | Link video YouTube/TikTok/IG (cột A Sheet) |
| shopee_link | TEXT | Link sản phẩm Shopee (cột C Sheet) |
| comment_text | TEXT | Text comment (cột D Sheet) |
| target_page_ids | TEXT | JSON array page_id đăng lên |
| scheduled_at | DATETIME | Giờ đặt lịch đăng (null = đăng ngay) |
| variant_mode | TEXT | `identical` / `auto_variant` |
| status | TEXT | pending / running / success / partial / failed / cancelled |
| created_at | DATETIME | |
| completed_at | DATETIME | Thời điểm hoàn tất toàn bộ batch |

### Bảng `post_logs` — Log chi tiết từng page

| Cột | Kiểu | Mô tả |
|---|---|---|
| id | INTEGER PK | |
| post_id | FK | Liên kết `posts.id` |
| page_id | FK | Liên kết `pages.id` |
| batch_index | INTEGER | Batch thứ mấy (1-5) |
| applied_caption | TEXT | Caption thực tế đã đăng (sau khi biến thể) |
| fb_post_id | TEXT | ID bài trên FB (dạng `pageId_postId`) |
| fb_post_url | TEXT | URL mở bài trên FB |
| comment_posted | BOOLEAN | Đã post comment chưa |
| fb_comment_id | TEXT | ID comment trên FB |
| error_message | TEXT | Lỗi nếu có |
| status | TEXT | success / failed |
| posted_at | DATETIME | |

### Bảng `sheets_config` — Config Google Sheets

| Cột | Kiểu | Mô tả |
|---|---|---|
| id | INTEGER PK | |
| sheet_id | TEXT | Google Sheet ID |
| tab_name | TEXT | Tên tab trong Sheet (mặc định `posts`) |
| last_synced_at | DATETIME | Lần đồng bộ Sheet gần nhất |
| is_active | BOOLEAN | |

### Bảng `settings` — Cài đặt chung

| Cột | Kiểu | Mô tả |
|---|---|---|
| key | TEXT PK | Tên setting |
| value | TEXT | Giá trị |

## 3.5: Chạy thử

```bash
streamlit run src/ui/app.py
```

→ Tự động mở browser ở `http://localhost:8501`

## Checklist Setup Project

- [ ] Tạo thư mục `fb-auto-post`
- [ ] Tạo virtual environment `venv`
- [ ] Kích hoạt venv thành công (dòng lệnh có `(venv)`)
- [ ] Tạo `requirements.txt`
- [ ] `pip install -r requirements.txt` chạy OK
- [ ] Tạo đầy đủ cấu trúc thư mục `src/`, `data/`, `logs/`
- [ ] Tạo file `.env` với App ID + App Secret
- [ ] Tạo `.gitignore`
- [ ] Tạo `src/main.py`, `src/config.py` skeleton

---

# 4. CÁC CHỨC NĂNG CẦN LÀM

Tool được chia thành **8 module** chính.

## 🎯 MODULE 1: QUẢN LÝ FANPAGE

### 1.1: Thêm Fanpage thủ công

- **Input**: Page ID, Tên page, Page Access Token
- **Xử lý**: 
  - Validate token bằng cách gọi `GET /{page_id}?fields=name,id`
  - Nếu trả về 200 OK → lưu vào bảng `pages`
  - Nếu 401/403 → báo token sai
- **UI**: Form có 3 trường + button "Thêm"

### 1.2: Import tự động từ User Token

- **Input**: User Access Token
- **Xử lý**:
  - Gọi `GET /me/accounts?fields=id,name,access_token`
  - Lưu tất cả page + token vào DB (upsert theo `page_id`)
- **UI**: 1 textarea để dán token + button "Import tất cả page"

### 1.3: Xem danh sách Page

| Cột | Kiểu |
|---|---|
| Tên page | Text |
| Page ID | Text |
| Trạng thái | Badge (Active/Paused) |
| Ngày thêm | Datetime |
| Hành động | Button (Edit, Toggle, Delete) |

### 1.4: Edit / Xóa / Tạm dừng page

- **Edit**: Update tên, token
- **Toggle**: Bật/tắt page
- **Delete**: Xóa hẳn khỏi DB (có confirm)

### 1.5: Cập nhật token khi hết hạn

- Khi đăng bài gặp 401 → đánh dấu page `token_expired`
- UI hiển thị cảnh báo, yêu cầu user update token

## 🎯 MODULE 2: GOOGLE SHEETS INTEGRATION

### 2.1: Config kết nối Sheet

- **Input**: Sheet ID, Tab name, đường dẫn `credentials.json`
- **Xử lý**:
  - Authorize bằng `google.oauth2.service_account.Credentials`
  - Mở Sheet qua `gspread.authorize(creds).open_by_key(sheet_id)`
  - Verify tab tồn tại, header đúng 7 cột (A–G)
- **Lưu vào**: Bảng `sheets_config`

### 2.2: Đọc danh sách bài chưa đăng

```python
# src/services/sheets_client.py
def fetch_pending_posts() -> list[SheetRow]:
    """Lấy các dòng có used = FALSE."""
    rows = sheet.get_all_records()
    return [
        SheetRow(row_index=i+2, **r)
        for i, r in enumerate(rows)
        if str(r.get("used", "")).upper() != "TRUE"
    ]
```

Trong UI **Tạo bài đăng** (Module 3), bạn sẽ chọn 1 row từ danh sách này.

### 2.3: Update Sheet sau khi đăng

Sau khi đăng xong 1 post (tất cả 50 page hoàn thành):

| Cột | Update |
|---|---|
| E `used` | `TRUE` |
| F `posted_at` | Thời điểm hiện tại |
| G `fb_post_ids` | JSON `{page_id: fb_post_id}` cho từng page đăng thành công |

```python
sheet.update(f"E{row_index}:G{row_index}", [[
    "TRUE",
    datetime.now().strftime("%Y-%m-%d %H:%M"),
    json.dumps(fb_post_ids_by_page)
]])
```

### 2.4: Preview row trước khi đăng

UI hiển thị:

- Caption (cột B)
- Thumbnail từ link video (nếu có) — dùng `oEmbed` API của YT/TikTok
- Link Shopee (cột C) — preview thumbnail sản phẩm nếu có
- Text comment (cột D)

### 2.5: Xử lý lỗi Sheet

| Lỗi | Cách xử lý |
|---|---|
| `credentials.json` sai/thiếu | UI báo, hướng dẫn tạo lại |
| Service account chưa được share | UI báo kèm email service account để user share |
| Sheet ID sai | Báo lỗi cụ thể |
| Header thiếu cột | Báo rõ cột nào thiếu, có nút "Tạo header tự động" |
| Sheet quota (429) | Retry với exponential backoff (1s, 2s, 4s) |

## 🎯 MODULE 3: TẠO BÀI ĐĂNG (từ Google Sheet)

### 3.1: Chọn nguồn bài

UI hiển thị bảng các row `used = FALSE` từ Sheet:

| Row | Caption | Video link | Shopee link | Comment |
| --- | --- | --- | --- | --- |
| 2 | Chị em xem review son này nè 😍 | youtu.be/abc | s.shopee.vn/xyz | Link mua nha chị em |
| 3 | Mặt nạ giá rẻ mà xịn | tiktok.com/... | s.shopee.vn/def | Mình dùng 1 tháng rồi |

Click 1 row → load vào form (các trường pre-fill, có thể sửa trước khi đăng).

### 3.2: Form tạo bài

| Trường | Nguồn | Mô tả |
|---|---|---|
| Caption | Từ Sheet (sửa được) | Nội dung bài đăng trên FB |
| Video link | Từ Sheet (sửa được) | Sẽ paste vào cuối caption để FB render preview |
| Shopee link | Từ Sheet (sửa được) | Link sản phẩm cho comment |
| Comment text | Từ Sheet (sửa được) | Text comment, sẽ nối với Shopee link |
| Chọn pages đăng lên | Multi-select | Default: chọn tất cả 50 page active |
| Batch size | Number (default 10) | Số page chạy song song / batch |
| Delay giữa batch (giây) | Slider (180–300) | Random trong khoảng |
| Biến thể nội dung | Toggle | Mặc định **ON** (khuyến nghị) / OFF = đăng y hệt |
| Chế độ | Radio | ⚡ Đăng ngay / ⏰ Đặt lịch |
| Thời gian đăng | Datetime picker | Khi chọn "Đặt lịch" |

### 3.3: Biến thể nội dung (khi toggle ON)

Mặc định **ON** để tránh FB flag duplicate khi đăng 50 page cùng 1 lúc.

**Cơ chế biến thể** (`src/services/variant.py`):

- **Emoji đầu/cuối**: random 1 trong 5 bộ emoji set
- **Câu mở đầu**: random 1 trong 5 template (vd: "Chị em ơi", "Mom nào đang tìm", "Hôm nay mình chia sẻ", ...)
- **Câu kết**: random 1 trong 5 template (vd: "Link ở comment nha", "Ai cần inbox mình", ...)
- **Hashtag**: random 1 trong 3 bộ hashtag

Kết quả: 50 page nhận 50 version **khác nhau ~5–10%** nhưng cốt lõi vẫn là caption gốc.

Khi OFF: 50 page nhận caption y hệt từ Sheet (rủi ro cao, chỉ dùng khi cần thiết).

### 3.4: Xây caption cuối cùng gửi lên FB

```python
def build_final_caption(base_caption: str, video_link: str, variant: bool) -> str:
    text = apply_variant(base_caption) if variant else base_caption
    return f"{text}\n\n{video_link}"
```

FB sẽ tự render preview (thumbnail + play button) cho link video.

### 3.5: Preview trước khi đăng

- Caption mẫu (1 version biến thể random để user xem)
- Thumbnail video từ oEmbed
- Danh sách 50 page sẽ đăng
- Comment text + Shopee link
- Dự kiến thời gian hoàn thành (50 page / 10 batch-size = 5 batch × ~4 phút/batch ≈ 20 phút)

### 3.6: Xác nhận & đăng

- Lưu vào bảng `posts` với `status = pending`, liên kết `sheet_row_index`
- Nếu "Đăng ngay" → push vào `batch_runner`
- Nếu "Đặt lịch" → APScheduler trigger khi tới giờ

## 🎯 MODULE 4: ENGINE ĐĂNG BÀI + COMMENT (Batch mode)

### 4.1: Chiến lược đăng — Cấp 2 Cân bằng

```text
50 page → chia 5 batch × 10 page
│
├─ Batch 1 (10 page chạy song song qua ThreadPoolExecutor)
│     ├─ Page 1: build caption (variant) → post → sleep 2-8s → comment
│     ├─ Page 2: build caption (variant) → post → sleep 2-8s → comment
│     └─ ... (10 page concurrent)
│
├─ Delay 180-300 giây (random)
│
├─ Batch 2 (10 page khác)
│
└─ ... Tổng: ~20 phút cho 50 page
```

### 4.2: Đăng bài (caption + video link)

Bài đăng dạng **text với link video** — FB tự render preview. KHÔNG upload video native.

```python
def post_to_page(page: Page, caption: str, video_link: str) -> str:
    final_text = f"{caption}\n\n{video_link}"
    res = requests.post(
        f"{FB_API_BASE}/{page.page_id}/feed",
        data={"message": final_text, "access_token": page.access_token},
        timeout=30,
    )
    res.raise_for_status()
    return res.json()["id"]  # dạng "pageId_postId"
```

### 4.3: Đăng 1 comment sau bài

```python
def post_comment(page: Page, fb_post_id: str, comment_text: str, shopee_link: str):
    time.sleep(random.uniform(MIN_COMMENT_DELAY, MAX_COMMENT_DELAY))
    final_comment = f"{comment_text}\n{shopee_link}"
    res = requests.post(
        f"{FB_API_BASE}/{fb_post_id}/comments",
        data={"message": final_comment, "access_token": page.access_token},
        timeout=30,
    )
    res.raise_for_status()
    return res.json()["id"]
```

### 4.4: Batch Runner — song song 10 page/batch

```python
# src/services/batch_runner.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import islice

def run_post_campaign(post: Post, pages: list[Page]):
    batches = list(chunked(pages, BATCH_SIZE))  # 10 page / batch
    
    for batch_idx, batch in enumerate(batches, 1):
        with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
            futures = {
                executor.submit(post_one_page, post, page, batch_idx): page
                for page in batch
            }
            for future in as_completed(futures):
                page = futures[future]
                try:
                    log_success(post, page, future.result())
                    update_progress()
                except Exception as e:
                    log_failure(post, page, e)
        
        # Delay giữa batch (không áp dụng cho batch cuối)
        if batch_idx < len(batches):
            time.sleep(random.uniform(MIN_BATCH_DELAY, MAX_BATCH_DELAY))
    
    # Hoàn tất → update Sheet
    sheets_client.mark_row_done(post.sheet_row_index, collected_fb_ids)
```

### 4.5: Post 1 page (trong batch)

```python
def post_one_page(post: Post, page: Page, batch_idx: int) -> dict:
    # Stagger nhẹ để không burst 10 request cùng 1 nanosecond
    time.sleep(random.uniform(MIN_PAGE_DELAY_IN_BATCH, MAX_PAGE_DELAY_IN_BATCH))
    
    # Biến thể caption nếu bật
    caption = apply_variant(post.caption) if post.variant_mode == "auto_variant" else post.caption
    
    fb_post_id = post_to_page(page, caption, post.video_link)
    fb_comment_id = post_comment(page, fb_post_id, post.comment_text, post.shopee_link)
    
    return {
        "fb_post_id": fb_post_id,
        "fb_post_url": f"https://facebook.com/{fb_post_id.replace('_', '/posts/')}",
        "applied_caption": caption,
        "fb_comment_id": fb_comment_id,
    }
```

### 4.6: Cập nhật Sheet sau khi hoàn tất

Khi toàn bộ 5 batch xong:

```python
sheets_client.update_row(
    row_index=post.sheet_row_index,
    used=True,
    posted_at=datetime.now(),
    fb_post_ids={page.page_id: log.fb_post_id for log in post.logs if log.status == "success"},
)
```

### 4.7: Progress UI realtime (Streamlit)

- Progress bar tổng: `completed_pages / total_pages`
- Status text: `Batch 2/5 — đang chạy 10 page...`
- Bảng live: mỗi page → ✅/❌ + FB post URL / error message
- Countdown giữa batch: `⏳ Chờ 2:45 trước batch tiếp theo`

### 4.8: Xử lý lỗi

| Lỗi | Hành động |
|---|---|
| Token hết hạn (401 / #190) | Pause page đó, log, báo user, tiếp page khác |
| Rate limit (#4, #17) | Delay gấp đôi, retry 1 lần trong batch; nếu vẫn fail → skip |
| Page bị hạn chế (#368) | Skip page, log cảnh báo "page có thể đang bị FB hạn chế" |
| Network timeout | Retry 3 lần với backoff 2s/4s/8s |
| Sheet update fail (quota) | Retry backoff; nếu vẫn fail → log để user update thủ công |
| Fail >50% 1 batch | Pause toàn bộ, yêu cầu user xem log trước khi tiếp |

### 4.9: Dry Run mode

- Toggle trong Settings
- Khi bật: KHÔNG gọi FB API, chỉ log ra caption / comment / thứ tự batch sẽ chạy
- Hữu ích test variant logic, batch logic trước khi chạy thật

## 🎯 MODULE 5: ĐẶT LỊCH ĐĂNG BÀI

### 5.1: Background scheduler

- Dùng **APScheduler** chạy background thread
- Mỗi 60s check bảng `posts`:
  ```sql
  SELECT * FROM posts 
  WHERE scheduled_at <= NOW() 
    AND status = 'pending'
  ```
- Với mỗi bài tìm được → trigger đăng

### 5.2: Đặt lịch theo chu kỳ

- **Đăng 1 lần** vào thời điểm cụ thể
- **Đăng hàng ngày** vào giờ X
- **Đăng theo tuần** (chọn các ngày trong tuần)
- **Đăng theo tháng** (ngày cụ thể trong tháng)

### 5.3: Xem danh sách lịch

- Nội dung bài (rút gọn)
- Thời gian đăng
- Số page sẽ đăng
- Status (pending/done/cancelled)
- Nút **Hủy lịch**

### 5.4: Hủy / Sửa lịch

- Xóa job khỏi scheduler
- Update DB `status = cancelled`

## 🎯 MODULE 6: XEM LỊCH SỬ & DASHBOARD

### 6.1: Dashboard tổng quan

- 📊 Tổng bài đăng **hôm nay / tuần này / tháng này**
- ✅ Tỷ lệ **thành công** (%)
- ❌ Số bài **thất bại**
- 💬 Tổng comment đã post
- 📈 Biểu đồ cột: số bài theo ngày (7 ngày gần nhất)
- 🏆 Top 5 page hoạt động nhiều nhất

### 6.2: Lịch sử chi tiết

Bảng với filter:

- Theo ngày (date range)
- Theo page
- Theo status (all / success / partial / failed)
- Search theo caption hoặc Shopee link
- Filter theo `sheet_row_index` (tìm lại bài đã đăng từ Sheet row nào)

Mỗi dòng hiển thị:

- **Caption** (rút gọn)
- **Thumbnail video** gốc (từ link YouTube/TikTok oEmbed)
- **Link video gốc** — click mở tab mới
- **Số page success / total** (vd: 48/50)
- **Ngày đăng**
- Button **"Xem chi tiết"**

Click 1 bài → modal chi tiết:

- Caption gốc + video link + Shopee link
- Bảng 50 page với các cột:
  - Tên page
  - Caption thực tế đã đăng (sau biến thể)
  - Status (✅/❌)
  - **Link FB post** (mở bài trên Facebook)
  - **Comment đã post** (text + Shopee link)
  - Lỗi (nếu có)
- Link mở lại **Sheet row** gốc

### 6.3: Export log

Export ra file **CSV** / **Excel**

## 🎯 MODULE 7: CÀI ĐẶT (SETTINGS)

### 7.1: Google Sheets

| Setting | Kiểu | Mô tả |
|---|---|---|
| Credentials file | File upload | Upload `credentials.json` → lưu vào `data/` |
| Sheet ID | Text | Copy từ URL Sheet |
| Tab name | Text | Mặc định `posts` |
| Test connection | Button | Thử mở Sheet + verify 7 cột header |
| Sync now | Button | Fetch pending rows ngay |

### 7.2: Batch posting

| Setting | Kiểu | Mặc định |
|---|---|---|
| Batch size | Number | 10 page / batch |
| Min delay giữa batch (giây) | Number | 180 |
| Max delay giữa batch (giây) | Number | 300 |
| Min delay trong batch (giây) | Number | 2 |
| Max delay trong batch (giây) | Number | 8 |
| Min delay comment (giây) | Number | 15 |
| Max delay comment (giây) | Number | 30 |

### 7.3: Nội dung & an toàn

| Setting | Kiểu | Mặc định |
|---|---|---|
| Biến thể nội dung mặc định | Toggle | On |
| Giới hạn bài/page/ngày | Number | 20 |
| Tự động retry khi lỗi | Toggle | On |
| Số lần retry tối đa | Number | 3 |
| Dry Run mode | Toggle | Off |

### 7.2: Backup / Restore DB

- **Backup**: Copy file `posts.db` ra thư mục backup (có timestamp)
- **Restore**: Upload file `.db` để khôi phục
- **Auto backup**: Hàng ngày lúc X giờ

### 7.3: Clear data

- Xóa log cũ hơn N ngày
- Xóa ảnh upload cũ

## 🎯 MODULE 8: BUILD `.EXE`

### 8.1: Lệnh build cơ bản

```bash
pyinstaller --onefile --windowed ^
  --name "FBAutoPost" ^
  --icon=assets/icon.ico ^
  --add-data "src/ui;src/ui" ^
  --add-data ".env;." ^
  src/main.py
```

### 8.2: File `build.bat` tự động hóa

```batch
@echo off
echo Cleaning old build...
rmdir /s /q build
rmdir /s /q dist

echo Building...
pyinstaller --onefile --windowed --name "FBAutoPost" --icon=assets/icon.ico src/main.py

echo Copying config files...
copy .env.example dist\
copy README.md dist\

echo Done! File at dist\FBAutoPost.exe
pause
```

### 8.3: Test file `.exe`

- Copy `FBAutoPost.exe` sang máy khác (không cài Python)
- Double-click chạy
- Kiểm tra:
  - Browser tự mở `localhost:8501`
  - DB `posts.db` được tạo trong cùng thư mục
  - Tất cả chức năng hoạt động

## Tóm tắt các module

| Module | Tên | Độ ưu tiên |
|---|---|---|
| 1 | Quản lý Fanpage | 🔴 Cao |
| 2 | Mẫu Comment | 🔴 Cao |
| 3 | Tạo Bài Đăng | 🔴 Cao |
| 4 | Engine Đăng + Comment | 🔴 Cao |
| 5 | Đặt Lịch | 🟡 Trung bình |
| 6 | Dashboard & Lịch sử | 🟡 Trung bình |
| 7 | Cài đặt | 🟢 Thấp |
| 8 | Build `.exe` | 🟢 Làm cuối |

---

# 5. LỘ TRÌNH PHÁT TRIỂN

Tổng thời gian dự kiến: **~6.5 ngày** cho 1 người full-time.

## Sprint 1 — Foundation (1 ngày)

**Mục tiêu**: Dựng nền tảng project, DB, module quản lý page.

### Tasks

- [ ] Setup virtual environment + cài thư viện
- [ ] Tạo cấu trúc thư mục đầy đủ
- [ ] Tạo file `.env`, `.env.example`, `.gitignore`
- [ ] Tạo `src/config.py` — load biến môi trường
- [ ] Tạo `src/database.py` — khởi tạo SQLAlchemy + tạo bảng
- [ ] Tạo 4 models: `Page`, `Post`, `PostLog`, `CommentTemplate`
- [ ] Tạo `src/services/fb_client.py` — wrapper cơ bản
- [ ] Module 1: Quản lý Fanpage (UI + CRUD)

### Deliverable
UI Streamlit có tab "Fanpages" với đầy đủ chức năng thêm/sửa/xóa/import page.

## Sprint 2 — Google Sheets Integration + UI Core (1 ngày)

**Mục tiêu**: Kết nối Sheet làm nguồn nội dung + dựng layout UI chính.

### Tasks

- [ ] Module 2: Google Sheets client (auth, fetch pending, update row)
- [ ] Form config Sheet (credentials upload, Sheet ID, test connection)
- [ ] Tạo layout Streamlit với sidebar menu:
  - 📋 Fanpages
  - 📊 Google Sheet
  - ✏️ Tạo Bài
  - ⏰ Lịch Đăng
  - 📜 Lịch Sử
  - ⚙️ Cài Đặt

### Deliverable

UI hoàn chỉnh với sidebar, kết nối được Sheet, đọc list pending rows.

## Sprint 3 — Engine Đăng Bài Batch Mode (2 ngày)

**Mục tiêu**: Core functionality — đăng 50 page theo batch + 1 comment/page.

### Tasks Ngày 1

- [ ] Module 3: Form tạo bài từ Sheet row (pre-fill caption, video, Shopee)
- [ ] Service `variant.py`: biến thể emoji/câu mở-kết/hashtag
- [ ] Preview caption + thumbnail video (oEmbed YT/TikTok)

### Tasks Ngày 2

- [ ] Module 4: Engine đăng bài batch mode
  - `poster.py`: post 1 page (caption + video link) + 1 comment (text + Shopee link)
  - `batch_runner.py`: ThreadPoolExecutor 10 page/batch, delay 3–5 phút giữa batch
  - Retry logic + error handling
  - Progress bar realtime theo batch
- [ ] Service `sheets_client.py`: update row sau khi đăng xong
- [ ] Test với **2 page Dry Run** → **1 batch thật 10 page** → **full 50 page**

### Deliverable

Click 1 Sheet row → tool đăng lên 50 page theo batch → update Sheet cột E/F/G.

## Sprint 4 — Đặt Lịch (1 ngày)

### Tasks

- [ ] Module 5: APScheduler background
- [ ] Form đặt lịch trong UI tạo bài
- [ ] Tab "Lịch Đăng": xem/sửa/hủy lịch
- [ ] Support đăng hàng ngày / hàng tuần

### Deliverable
Đặt được lịch đăng cho tương lai, tool tự trigger khi đến giờ.

## Sprint 5 — Dashboard & History (1 ngày)

### Tasks

- [ ] Module 6: Dashboard (card metrics, biểu đồ Plotly, top page)
- [ ] Tab Lịch sử (bảng + filter + modal chi tiết)
- [ ] Export CSV/Excel

### Deliverable
Dashboard đầy đủ, user biết rõ tool đã làm gì.

## Sprint 6 — Settings + Build (0.5 ngày)

### Tasks

- [ ] Module 7: Settings
- [ ] Module 8: Build `.exe` với PyInstaller
- [ ] Test `.exe` trên máy clean

### Deliverable
File `FBAutoPost.exe` chạy được trên máy không cài Python.

## Milestones

| Milestone | Sau sprint | Kết quả |
|---|---|---|
| **M1: Foundation ready** | Sprint 1 | Quản lý page |
| **M2: UI ready** | Sprint 2 | Giao diện đầy đủ |
| **M3: Core ready** | Sprint 3 | Đăng bài + comment tự động |
| **M4: Scheduler ready** | Sprint 4 | Đặt lịch hoạt động |
| **M5: Full features** | Sprint 5 | Dashboard + lịch sử |
| **M6: Released** | Sprint 6 | File `.exe` sẵn sàng dùng |

## MVP (Tối thiểu để dùng được)

Nếu muốn rút ngắn, MVP chỉ cần **Sprint 1 + 2 + 3** (~4 ngày):

- Quản lý 50+ page từ nhiều tài khoản
- Kết nối Google Sheet làm nguồn nội dung
- Đăng 1 row Sheet → 50 page theo batch + 1 comment Shopee/page
- Update Sheet tự động sau khi đăng (không có đặt lịch)

---

# 6. LƯU Ý QUAN TRỌNG & BẢO MẬT

## 6.1: Tránh bị Facebook chặn / giảm reach

### Giới hạn khuyến nghị (Cấp 2 — Cân bằng)

| Hành vi | Giới hạn an toàn |
|---|---|
| Batch size | **10 page** chạy song song / batch |
| Delay giữa các batch | **180–300 giây** (3–5 phút, random) |
| Delay trong 1 batch | **2–8 giây** stagger giữa các page |
| Delay comment sau post | **15–30 giây** (random) |
| Số comment / bài | **1 comment** (link Shopee) |
| Số bài đăng / page / ngày | **< 20 bài** |
| Số lần đăng liên tiếp trong giờ | **< 5 bài / page** |
| Tổng thời gian đăng 50 page | **~20 phút / đợt** |

### Best practices

- ✅ **Bật Biến thể nội dung** (mặc định ON) — 50 page nhận 50 version hơi khác nhau
- ✅ **Mỗi Sheet row = 1 sản phẩm/video** → comment Shopee phải match đúng sản phẩm
- ✅ **Dùng link rút gọn** Shopee (`s.shopee.vn/...`) thay vì URL dài
- ✅ **Đăng vào giờ cao điểm**: 7–9h sáng, 12–13h trưa, 19–22h tối
- ✅ **Giãn giữa các đợt đăng** — nếu đăng đợt 2 trong ngày, cách đợt 1 ≥ 3 tiếng
- ✅ **Xem log Dashboard** sau mỗi đợt — nếu >10% page fail → dừng lại điều tra

### Những thứ cần tránh

- ❌ **Đăng y hệt 100%** trên 50 page cùng 1 thời điểm (tắt biến thể chỉ khi thực sự cần)
- ❌ Comment có **nhiều emoji liên tục** (5+ emoji cạnh nhau)
- ❌ **Từ khóa nhạy cảm**: "mua ngay", "giảm 90%", "CLICK NGAY", viết hoa toàn bộ
- ❌ **Giảm delay giữa batch** xuống dưới 180 giây → dễ bị flag coordinated behavior
- ❌ **Tăng batch size** lên trên 10 → 15+ page song song dễ bị soi
- ❌ **Đăng 24/7 không nghỉ** → tạo pattern bất thường
- ❌ **Cùng 1 link Shopee** cho nhiều sản phẩm khác nhau → FB dễ phát hiện affiliate spam

## 6.2: Bảo mật

### Không bao giờ commit / share các file sau

- `.env` — chứa App Secret + Google Sheet ID
- `data/credentials.json` — Google Service Account key (bị lộ = mất quyền access Sheet)
- `data/posts.db` — chứa tất cả Page Access Token + dữ liệu đăng
- `data/uploads/` — có thể chứa ảnh nhạy cảm
- `logs/app.log` — có thể lộ token

### Google Service Account

- Nếu `credentials.json` **bị lộ** → vào Cloud Console → **Delete Key cũ + tạo Key mới** → thay file trong `data/`
- Share Sheet chỉ cho đúng **email service account**, KHÔNG share public
- Mỗi project nên có **1 service account riêng**, đừng reuse

### Access Token

- **Page Access Token** của page bạn là admin → không hết hạn
- Nhưng nếu **đổi password FB** → token bị invalidate → cần lấy lại
- Nếu **App Secret bị lộ** → vào developers.facebook.com → Reset Secret ngay

## 6.3: Debug & Log

### Log level khuyến nghị

| Môi trường | Log level |
|---|---|
| Development | `DEBUG` — log full request/response |
| Production (file .exe) | `INFO` — log sự kiện chính |

### Mask token trong log

```python
def mask_token(token: str) -> str:
    if len(token) < 10:
        return "***"
    return token[:6] + "..." + token[-4:]
```

### Dry Run Mode

- Toggle trong Settings
- Khi bật: KHÔNG gọi API thật, chỉ log ra các bước sẽ làm
- Dùng để test logic mà không đăng bài thật

## 6.4: Backup

- File `data/posts.db` — chứa tất cả page, template, log
- Backup tự động hàng ngày
- Giữ lại 7–14 bản backup gần nhất

## 6.5: Troubleshooting — Lỗi thường gặp

| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| `(#200) Requires pages_manage_posts permission` | Thiếu permission | Xin lại permission ở App Review |
| `(#100) Tried accessing nonexisting field` | Page ID sai | Kiểm tra lại page ID |
| `(#190) Error validating access token` | Token sai/hết hạn | Lấy token mới |
| `(#4) Application request limit reached` | Rate limit | Tăng delay, chờ 1 giờ |
| `(#17) User request limit reached` | User-level rate limit | Dùng page token khác |
| `(#368) The action attempted has been deemed abusive` | Bị coi là spam | Giảm tần suất, đa dạng hóa nội dung |
| `HTTPSConnectionPool timeout` | Mạng chậm/không ổn | Retry với delay tăng dần |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Lỗi SSL Windows | Update Python, cài certifi |
| `streamlit: command not found` | Chưa kích hoạt venv | `venv\Scripts\activate` |

### Khi tool không hoạt động

1. **Xem log** tại `logs/app.log`
2. **Kiểm tra FB token** có còn valid không (thử Graph API Explorer)
3. **Test Google Sheet connection** ở tab Settings → Test connection
4. **Verify Sheet header** đúng 7 cột (A–G) + service account đã được share
5. **Test Dry Run** để xem logic biến thể + batch đúng chưa
6. **Kiểm tra kết nối mạng** và firewall
7. **Update thư viện** nếu lâu chưa update:

   ```bash
   pip install -r requirements.txt --upgrade
   ```

## 6.6: Tài liệu tham khảo

- Facebook Graph API: <https://developers.facebook.com/docs/graph-api>
- Page Posts API: <https://developers.facebook.com/docs/pages-api/posts>
- Page Comments API: <https://developers.facebook.com/docs/graph-api/reference/v19.0/object/comments>
- Google Sheets API: <https://developers.google.com/sheets/api>
- gspread docs: <https://docs.gspread.org>
- Streamlit docs: <https://docs.streamlit.io>
- SQLAlchemy docs: <https://docs.sqlalchemy.org>
- APScheduler docs: <https://apscheduler.readthedocs.io>
- PyInstaller docs: <https://pyinstaller.org>

## 6.7: Pháp lý

- Tool này chỉ dùng để **đăng bài lên page DO BẠN QUẢN LÝ**
- Không dùng để: spam page/nhóm người khác, tự động kết bạn hàng loạt, scrape dữ liệu, fake engagement
- Tuân thủ [Facebook Platform Terms](https://developers.facebook.com/terms) và [Community Standards](https://transparency.fb.com/policies/community-standards/)

---

## Tác giả

- Email: fbshopcloud@gmail.com
- Ngày tạo: 2026-04-22
