# FB Auto Post Tool

Tool desktop tự động đăng bài và comment lên nhiều Facebook Fanpage do bạn quản lý.

## Tính năng chính

- ✅ Đăng bài (text + ảnh) lên nhiều Fanpage cùng lúc
- ✅ Tự động comment 5–10 comment có sẵn (gắn link Shopee / affiliate) vào bài vừa đăng
- ✅ Đặt lịch đăng bài theo giờ / ngày
- ✅ Quản lý template comment theo nhóm
- ✅ Xem lịch sử, thống kê, log chi tiết
- ✅ Build thành file `.exe` dùng trên Windows (không cần cài Python)

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.11+ |
| UI | Streamlit |
| Database | SQLite (SQLAlchemy ORM) |
| HTTP Client | Requests |
| Lập lịch | APScheduler |
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

1. [Hướng dẫn cài đặt môi trường](#1-hướng-dẫn-cài-đặt-môi-trường)
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

## Checklist Setup

- [ ] Cài Python 3.11+ và tick "Add to PATH"
- [ ] `python --version` chạy được ở terminal mới
- [ ] Cài VS Code + extension Python + SQLite Viewer
- [ ] Tạo Facebook App type Business
- [ ] Có **App ID** và **App Secret**
- [ ] Lấy được **User Access Token** từ Graph API Explorer
- [ ] Gọi `/me/accounts` lấy được **Page Access Token** cho từng page
- [ ] (Tùy) Convert sang Long-lived Token

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
python -c "import requests, streamlit, sqlalchemy, PIL, apscheduler; print('OK')"
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

```
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
│   │   ├── post.py                # Model bài đăng
│   │   ├── post_log.py            # Model log
│   │   └── comment_template.py    # Model mẫu comment
│   ├── services/
│   │   ├── __init__.py
│   │   ├── fb_client.py           # Wrapper gọi Graph API
│   │   ├── poster.py              # Logic đăng bài + comment
│   │   ├── scheduler.py           # APScheduler background
│   │   └── image_utils.py         # Resize, nén ảnh
│   └── ui/
│       ├── __init__.py
│       ├── app.py                 # Streamlit entry point
│       ├── page_manager.py        # Tab quản lý fanpage
│       ├── post_creator.py        # Tab tạo bài đăng
│       ├── comment_templates.py   # Tab mẫu comment
│       ├── scheduler_view.py      # Tab lịch đăng
│       ├── history.py             # Tab lịch sử
│       └── settings.py            # Tab cài đặt
├── data/
│   ├── posts.db                   # SQLite DB (tự tạo khi chạy lần đầu)
│   └── uploads/                   # Ảnh user upload
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

# Database
DB_PATH=data/posts.db

# Uploads
UPLOAD_DIR=data/uploads
MAX_UPLOAD_SIZE_MB=10

# Logging
LOG_PATH=logs/app.log
LOG_LEVEL=INFO

# Delay mặc định (giây)
MIN_COMMENT_DELAY=15
MAX_COMMENT_DELAY=30
MIN_PAGE_DELAY=60
MAX_PAGE_DELAY=120

# Giới hạn
MAX_POSTS_PER_PAGE_PER_DAY=20
MAX_COMMENTS_PER_POST=10
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

FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
FB_API_VERSION = os.getenv("FB_API_VERSION", "v19.0")
FB_API_BASE = f"https://graph.facebook.com/{FB_API_VERSION}"

DB_PATH = BASE_DIR / os.getenv("DB_PATH", "data/posts.db")
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "data/uploads")
LOG_PATH = BASE_DIR / os.getenv("LOG_PATH", "logs/app.log")

MIN_COMMENT_DELAY = int(os.getenv("MIN_COMMENT_DELAY", 15))
MAX_COMMENT_DELAY = int(os.getenv("MAX_COMMENT_DELAY", 30))
MIN_PAGE_DELAY = int(os.getenv("MIN_PAGE_DELAY", 60))
MAX_PAGE_DELAY = int(os.getenv("MAX_PAGE_DELAY", 120))

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

### Bảng `posts` — Lưu bài đăng

| Cột | Kiểu | Mô tả |
|---|---|---|
| id | INTEGER PK | |
| content | TEXT | Nội dung bài |
| image_paths | TEXT | JSON array các ảnh |
| target_page_ids | TEXT | JSON array page_id đăng lên |
| comment_template_group | TEXT | Nhóm template dùng |
| comments_per_post | INTEGER | Số comment mỗi bài (5-10) |
| scheduled_at | DATETIME | Giờ đặt lịch đăng |
| status | TEXT | pending / running / success / failed / cancelled |
| created_at | DATETIME | |

### Bảng `post_logs` — Log chi tiết từng page

| Cột | Kiểu | Mô tả |
|---|---|---|
| id | INTEGER PK | |
| post_id | FK | Liên kết `posts.id` |
| page_id | FK | Liên kết `pages.id` |
| fb_post_id | TEXT | ID bài trên FB (dạng `pageId_postId`) |
| comments_posted | INTEGER | Số comment đã đăng |
| error_message | TEXT | Lỗi nếu có |
| status | TEXT | success / failed |
| posted_at | DATETIME | |

### Bảng `comment_templates` — Mẫu comment

| Cột | Kiểu | Mô tả |
|---|---|---|
| id | INTEGER PK | |
| content | TEXT | Nội dung comment + link |
| group_name | TEXT | Nhóm (vd: "Shopee sức khỏe") |
| is_active | BOOLEAN | |
| created_at | DATETIME | |

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

## 🎯 MODULE 2: QUẢN LÝ MẪU COMMENT

### 2.1: Tạo template comment

- **Input**: Nội dung comment + Nhóm (vd: "Shopee sức khỏe", "TikTok Shop")
- **Lưu vào**: Bảng `comment_templates`

### 2.2: Quản lý template theo nhóm

- **List view**: hiển thị các nhóm + số lượng template mỗi nhóm
- **Detail view**: vào từng nhóm xem/sửa/xóa template
- **Search**: tìm template theo từ khóa

### 2.3: Import / Export template

- **Import**: Upload file `.txt` (mỗi dòng 1 comment), chọn nhóm → bulk insert
- **Export**: Xuất nhóm ra file `.txt` để backup

### 2.4: Preview comment

- Hiển thị preview text
- Nếu có link Shopee/TikTok → render thumbnail

## 🎯 MODULE 3: TẠO BÀI ĐĂNG

### 3.1: Form nhập bài

| Trường | Kiểu | Mô tả |
|---|---|---|
| Nội dung bài | Textarea | Nội dung post |
| Ảnh | File upload | 1 hoặc nhiều ảnh |
| Chọn pages đăng lên | Multi-select | Checkbox nhiều page |
| Nhóm comment | Select | Chọn 1 nhóm template |
| Số lượng comment | Number input | 5–10, random |
| Delay giữa comment | Slider | 15–60 giây |
| Delay giữa page | Slider | 60–300 giây |
| Chế độ | Radio | ⚡ Đăng ngay / ⏰ Đặt lịch |
| Thời gian đăng | Datetime picker | Khi chọn "Đặt lịch" |

### 3.2: Xử lý ảnh trước khi upload

- **Resize** về max 1200px chiều dài
- **Convert** HEIC/HEIF → JPG
- **Nén** quality 85%
- **Giới hạn** 10MB mỗi ảnh

### 3.3: Preview bài đăng

- Nội dung bài
- Thumbnail các ảnh
- Danh sách page sẽ đăng lên
- 5–10 comment random từ nhóm đã chọn
- Dự kiến thời gian hoàn thành

### 3.4: Xác nhận & đăng

- Lưu vào bảng `posts` với `status = pending`
- Nếu "Đăng ngay" → push vào queue background
- Nếu "Đặt lịch" → APScheduler trigger khi tới giờ

## 🎯 MODULE 4: ENGINE ĐĂNG BÀI + COMMENT

### 4.1: Upload ảnh lên Facebook

Gọi `POST /{page_id}/photos` với `published=false`, lấy `photo_id`

### 4.2: Đăng bài

**Case 1: Chỉ text**
```
POST /{page_id}/feed
  message={content}
  access_token={page_token}
```

**Case 2: 1 ảnh + text**
```
POST /{page_id}/photos
  caption={content}
  source=@file.jpg
  access_token={page_token}
```

**Case 3: Nhiều ảnh + text**

1. Upload từng ảnh với `published=false` → lấy list `photo_id`
2. Gọi:
```
POST /{page_id}/feed
  message={content}
  attached_media=[{"media_fbid":"photo_id_1"},{"media_fbid":"photo_id_2"}]
  access_token={page_token}
```

### 4.3: Loop comment tự động

- Lấy random 5–10 comment từ nhóm template
- Shuffle thứ tự
- Với mỗi comment:
  - Gọi `POST /{post_id}/comments`
  - Delay random 15–30s
  - Log thành công / thất bại
- Nếu 1 comment fail → skip, tiếp comment tiếp theo

### 4.4: Loop qua nhiều page

```
for page in selected_pages:
    try:
        post_id = upload_and_post(page)
        comment_loop(post_id, page)
    except Exception as e:
        log_error(page, e)
        continue
    
    delay(60-120s random)
```

Hiển thị **progress bar** realtime trên Streamlit UI.

### 4.5: Xử lý lỗi

| Lỗi | Hành động |
|---|---|
| Token hết hạn (401) | Pause page đó, log, báo user |
| Rate limit (#4, #17) | Delay gấp đôi, retry 1 lần |
| Page bị hạn chế | Skip, tiếp page khác |
| Network timeout | Retry 3 lần, delay tăng dần |
| Ảnh upload fail | Thử lại 2 lần, nếu vẫn fail → skip ảnh |

### 4.6: Dry Run mode

- Toggle để chạy giả lập (không gọi API thật)
- Log ra các bước sẽ làm để debug

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
- Theo status (all / success / failed)
- Search theo nội dung

Click 1 bài → modal chi tiết:
- Nội dung đã đăng
- Thumbnail ảnh
- Danh sách page + FB post ID (có **link mở Facebook**)
- Danh sách comment đã post + thời gian
- Lỗi (nếu có) + stack trace

### 6.3: Export log

Export ra file **CSV** / **Excel**

## 🎯 MODULE 7: CÀI ĐẶT (SETTINGS)

### 7.1: Cài đặt chung

| Setting | Kiểu | Mặc định |
|---|---|---|
| Delay comment min | Number | 15s |
| Delay comment max | Number | 30s |
| Delay page min | Number | 60s |
| Delay page max | Number | 120s |
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

## Sprint 2 — Comment Template + UI Core (1 ngày)

**Mục tiêu**: Quản lý template comment + dựng layout UI chính.

### Tasks

- [ ] Module 2: Quản lý mẫu comment
- [ ] Tạo layout Streamlit với sidebar menu:
  - 📋 Fanpages
  - 💬 Mẫu Comment
  - ✏️ Tạo Bài
  - ⏰ Lịch Đăng
  - 📊 Lịch Sử
  - ⚙️ Cài Đặt

### Deliverable
UI hoàn chỉnh với sidebar, có thể quản lý page + template.

## Sprint 3 — Engine Đăng Bài (2 ngày)

**Mục tiêu**: Core functionality — đăng bài + comment tự động.

### Tasks Ngày 1

- [ ] Module 3: Form tạo bài đăng
- [ ] Xử lý ảnh: resize, nén, convert HEIC

### Tasks Ngày 2

- [ ] Module 4: Engine đăng bài
  - `poster.py`: upload ảnh, đăng bài, comment loop
  - Retry logic + error handling
  - Progress bar realtime
- [ ] Test với **1 page** trước, sau đó **multi-page**

### Deliverable
Đăng được bài + comment tự động lên nhiều page.

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

- Quản lý page
- Quản lý comment
- Đăng bài + comment thủ công (không có đặt lịch)

---

# 6. LƯU Ý QUAN TRỌNG & BẢO MẬT

## 6.1: Tránh bị Facebook chặn / giảm reach

### Giới hạn khuyến nghị

| Hành vi | Giới hạn an toàn |
|---|---|
| Delay giữa các comment | **15–30 giây** (random) |
| Delay giữa các page | **60–120 giây** (random) |
| Số bài đăng / page / ngày | **< 20 bài** |
| Số comment / bài | **5–10 comment** |
| Số lần đăng liên tiếp trong giờ | **< 5 bài** |

### Best practices

- ✅ **Đa dạng nội dung comment** — ít nhất 20-30 mẫu khác nhau cho mỗi nhóm
- ✅ **Dùng link rút gọn** (s.shopee.vn, bit.ly)
- ✅ **Đăng vào giờ cao điểm**: 7-9h sáng, 12-13h trưa, 19-22h tối
- ✅ **Rải đều các page** — đừng đăng dồn 1 page trong thời gian ngắn

### Những thứ cần tránh

- ❌ Comment có **nhiều emoji liên tục** (5+ emoji cạnh nhau)
- ❌ **Từ khóa nhạy cảm**: "mua ngay", "giảm 90%", "CLICK NGAY", viết hoa toàn bộ
- ❌ **Post trùng nội dung y hệt** qua nhiều page cùng lúc
- ❌ **Delay quá ngắn** (< 10s) → dễ bị flag là bot
- ❌ **Đăng 24/7 không nghỉ** → tạo pattern bất thường

## 6.2: Bảo mật

### Không bao giờ commit / share các file sau

- `.env` — chứa App Secret
- `data/posts.db` — chứa tất cả Page Access Token
- `data/uploads/` — có thể chứa ảnh nhạy cảm
- `logs/app.log` — có thể lộ token

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
2. **Kiểm tra token** có còn valid không (thử Graph API Explorer)
3. **Test Dry Run** để xem logic đúng chưa
4. **Kiểm tra kết nối mạng** và firewall
5. **Update thư viện** nếu lâu chưa update:
   ```
   pip install -r requirements.txt --upgrade
   ```

## 6.6: Tài liệu tham khảo

- Facebook Graph API: https://developers.facebook.com/docs/graph-api
- Page Posts API: https://developers.facebook.com/docs/pages-api/posts
- Page Comments API: https://developers.facebook.com/docs/graph-api/reference/v19.0/object/comments
- Streamlit docs: https://docs.streamlit.io
- SQLAlchemy docs: https://docs.sqlalchemy.org
- APScheduler docs: https://apscheduler.readthedocs.io
- PyInstaller docs: https://pyinstaller.org

## 6.7: Pháp lý

- Tool này chỉ dùng để **đăng bài lên page DO BẠN QUẢN LÝ**
- Không dùng để: spam page/nhóm người khác, tự động kết bạn hàng loạt, scrape dữ liệu, fake engagement
- Tuân thủ [Facebook Platform Terms](https://developers.facebook.com/terms) và [Community Standards](https://transparency.fb.com/policies/community-standards/)

---

## Tác giả

- Email: fbshopcloud@gmail.com
- Ngày tạo: 2026-04-22
