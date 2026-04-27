# SETUP.md — Hướng dẫn cài đặt và sử dụng FB Auto Post Tool

Tài liệu này dành cho **người dùng cuối** (chủ shop affiliate, marketing manager). Theo từng bước, sau ~30 phút bạn có tool chạy trên máy + connect đa tài khoản FB + tự động đăng bài lên 50+ fanpage từ Google Sheets.

## Mục lục

1. [Yêu cầu hệ thống](#1-yêu-cầu-hệ-thống)
2. [Cài đặt môi trường (1 lần)](#2-cài-đặt-môi-trường-1-lần)
3. [Setup Facebook App](#3-setup-facebook-app)
4. [Setup Google Sheets](#4-setup-google-sheets)
5. [Cấu hình `.env`](#5-cấu-hình-env)
6. [Chạy tool lần đầu](#6-chạy-tool-lần-đầu)
7. [Connect các tài khoản Facebook](#7-connect-các-tài-khoản-facebook)
8. [Đăng bài đầu tiên](#8-đăng-bài-đầu-tiên)
9. [Đặt lịch + tự động hóa](#9-đặt-lịch--tự-động-hóa)
10. [Troubleshooting](#10-troubleshooting)
11. [(Optional) Deploy Cloudflare Worker — token vĩnh viễn](#11-optional-deploy-cloudflare-worker)

---

## 1. Yêu cầu hệ thống

- **Windows 10/11** (hoặc Mac/Linux)
- **Python 3.11** (file `.exe` build sẵn không cần cài Python)
- Trình duyệt **Chrome** hoặc **Edge**
- Tài khoản Google Cloud (free) + Facebook Developer (free)

---

## 2. Cài đặt môi trường (1 lần)

> Bỏ qua phần này nếu bạn nhận file `.exe` đã build sẵn.

### 2.1 Cài Python 3.11

1. Tải: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
2. Chạy installer → ⚠️ **TICK "Add Python to PATH"** trước khi Install
3. Mở PowerShell mới, gõ:

   ```powershell
   python --version
   ```

   Phải hiện `Python 3.11.x`.

### 2.2 Tải tool

```powershell
cd D:\YourFolder
git clone <repo-url> fb-auto-post
cd fb-auto-post
```

Hoặc tải file zip, giải nén.

### 2.3 Tạo virtual environment + cài thư viện

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

→ Đầu dòng terminal hiện `(venv)` là OK.

---

## 3. Setup Facebook App

### 3.1 Tạo App

1. Truy cập: https://developers.facebook.com/apps/
2. Bấm **Tạo ứng dụng** → chọn loại **Business** → Next
3. Điền:
   - App name: `FB Auto Post` (hoặc tên gì cũng được)
   - App contact email: email của bạn
4. Bấm **Tạo ứng dụng**

### 3.2 Add Use Case "Quản lý mọi thứ trên Trang"

1. Trong wizard tạo App → màn **Trường hợp sử dụng** → tab **Quản lý nội dung**
2. Tick: **Quản lý mọi thứ trên Trang**
3. Tiếp tục các bước, **Tạo ứng dụng**

### 3.3 Add các permissions cần thiết vào use case

1. Sidebar trái → **Trường hợp sử dụng**
2. Bấm **Tùy chỉnh** ở use case "Quản lý mọi thứ trên Trang"
3. Bấm **+ Thêm** ở các permission sau:
   - ✅ `pages_show_list`
   - ✅ `pages_manage_posts`
   - ✅ `pages_read_engagement`
   - ✅ `pages_manage_engagement`
   - ✅ `pages_read_user_content` (giúp tránh bug "Invalid Scopes")
4. Mỗi permission status phải là **"Sẵn sàng thử nghiệm"**

### 3.4 Setup Facebook Login for Business

1. Sidebar trái → **Đăng nhập bằng Facebook** → **Cài đặt**
2. Bật **Có** cho:
   - ✅ Đăng nhập OAuth ứng dụng
   - ✅ Đăng nhập OAuth trên web
   - ✅ Đăng nhập OAuth được nhúng trên trình duyệt
   - ✅ Chế độ sử dụng nghiêm ngặt cho URI chuyển hướng
3. Trong ô **URI chuyển hướng OAuth hợp lệ**, thêm:
   ```
   http://localhost:8765/callback
   ```
4. Bấm **Lưu thay đổi**

### 3.5 Lấy App ID + App Secret

1. Sidebar trái → **Cài đặt → Cơ bản**
2. Copy **ID ứng dụng** (15-16 chữ số)
3. Bấm **Hiển thị** ở **Khóa bí mật của ứng dụng** → nhập password FB → copy chuỗi
4. Lưu cả 2 vào file txt tạm thời để paste vào `.env` ở Bước 5

### 3.6 Add các tài khoản FB của bạn làm Tester

Trong **Development mode**, chỉ user là Admin/Tester của App mới OAuth được. Add các tài khoản FB còn lại:

1. Sidebar trái → **Vai trò trong ứng dụng → Vai trò**
2. Phần **Người dùng thử nghiệm** (Testers) → bấm **Thêm người**
3. Nhập Facebook ID hoặc username của tài khoản → Submit
4. Người được mời vào https://www.facebook.com/settings?tab=apps_and_websites → Accept

---

## 4. Setup Google Sheets

### 4.1 Tạo Google Cloud Project

1. https://console.cloud.google.com/projectcreate
2. Project name: `FB Auto Post`
3. Organization: chọn **No organization** (tránh policy block)
4. Create → đợi ~30s

### 4.2 Bật APIs

Mở 2 link, mỗi link bấm **Enable**:
- https://console.cloud.google.com/apis/library/sheets.googleapis.com
- https://console.cloud.google.com/apis/library/drive.googleapis.com

(Đảm bảo project ở header là `FB Auto Post`)

### 4.3 Tạo Service Account + tải `credentials.json`

1. https://console.cloud.google.com/iam-admin/serviceaccounts
2. **+ Create Service Account**
3. Name: `fb-auto-post-bot` → Create and Continue → để trống → Done
4. Click vào service account vừa tạo
5. Tab **Keys → Add Key → Create new key → JSON → Create**
6. File JSON tự download → đổi tên thành `credentials.json`
7. Để file vào thư mục `data/` của tool (sẽ làm sau)

### 4.4 Tạo Google Sheet

1. https://sheets.new → tên: `FB Content Queue`
2. Tab đầu tiên → đổi tên thành `posts`
3. Hàng 1 — gõ 7 cột header (chính xác, lowercase):

   | A | B | C | D | E | F | G |
   |---|---|---|---|---|---|---|
   | `video_link` | `caption` | `shopee_link` | `comment_text` | `used` | `posted_at` | `fb_post_ids` |

### 4.5 Share Sheet cho Service Account

1. Mở `credentials.json` bằng Notepad → tìm field `"client_email"` → copy giá trị (dạng `fb-auto-post-bot@xxx.iam.gserviceaccount.com`)
2. Mở Google Sheet → bấm **Share** (góc phải trên)
3. Paste email service account → đổi quyền **Editor** → bỏ tick "Notify people" → Send
4. Nếu Google warning *"This email isn't a Google Account"* → bấm **Share anyway**

### 4.6 Lấy Sheet ID

URL Sheet: `https://docs.google.com/spreadsheets/d/`**`SHEET_ID_NAY`**`/edit`

Copy phần `SHEET_ID_NAY` (chuỗi dài giữa `/d/` và `/edit`).

---

## 5. Cấu hình `.env`

Trong thư mục tool, copy `.env.example` thành `.env`:

```powershell
copy .env.example .env
```

Mở file `.env` bằng VS Code (hoặc Notepad), điền:

```env
# Facebook App (lấy từ Bước 3.5)
FB_APP_ID=<App ID 16 chữ số>
FB_APP_SECRET=<App Secret 32 ký tự>
FB_API_VERSION=v19.0

# Google Sheets
GOOGLE_CREDENTIALS_PATH=data/credentials.json
GOOGLE_SHEET_ID=<Sheet ID lấy từ Bước 4.6>
GOOGLE_SHEET_TAB=posts

# (Optional) Cloudflare Worker — chỉ điền khi deploy production, xem mục 11
OAUTH_BACKEND_URL=
OAUTH_REDIRECT_PORT=8765

# Các giá trị khác giữ default
DB_PATH=data/posts.db
LOG_PATH=logs/app.log
LOG_LEVEL=INFO

BATCH_SIZE=10
MIN_BATCH_DELAY=180
MAX_BATCH_DELAY=300
MIN_PAGE_DELAY_IN_BATCH=2
MAX_PAGE_DELAY_IN_BATCH=8
MIN_COMMENT_DELAY=15
MAX_COMMENT_DELAY=30
COMMENTS_PER_POST=1
MAX_POSTS_PER_PAGE_PER_DAY=20
ENABLE_CONTENT_VARIANT=true
```

Save file.

Copy `credentials.json` (từ Bước 4.3) vào thư mục `data/` của tool.

⚠️ **TUYỆT ĐỐI không commit `.env` và `credentials.json` lên Git** (đã có trong `.gitignore`).

---

## 6. Chạy tool lần đầu

```powershell
.\venv\Scripts\Activate.ps1
streamlit run src/ui/app.py
```

Lần đầu Streamlit hỏi email — bấm **Enter** để bỏ qua.

→ Browser tự mở `http://localhost:8501` với giao diện tool.

→ Sidebar trái có **7 tab**: Tài khoản FB, Fanpages, Google Sheet, Tạo Bài, Lịch Đăng, Lịch Sử, Cài Đặt.

---

## 7. Connect các tài khoản Facebook

### Bước 1: Mở tab "👥 Tài khoản FB"

Sidebar trái → click **Tài khoản FB**.

### Bước 2: Connect tài khoản đầu tiên

1. Bấm **➕ Thêm tài khoản FB**
2. Browser tự mở 1 tab mới → trang Facebook OAuth
3. Login Facebook (nếu chưa) → trang **"Auto Post Des đang yêu cầu quyền truy cập"**
4. ⚠️ Tick **TẤT CẢ checkbox** (đừng bỏ tick gì)
5. Bấm **Tiếp tục**
6. Trang **"Chọn các Trang để cấp quyền"** → chọn **"Tất cả các Trang hiện tại và sau này"** → Tiếp tục
7. Trang summary → bấm **Lưu**
8. Browser hiện trang **"✅ Đã đăng nhập thành công"** → đóng tab
9. Quay lại tool → toast hiện `✅ Đã connect <Tên bạn> (X pages, long-lived 60 ngày)`

→ Card tài khoản hiện ra với danh sách pages. **Page Token đã lưu vào DB**, không cần thao tác lại.

### Bước 3: Connect tài khoản thứ 2 (cùng máy)

Vấn đề: browser đang giữ session tài khoản 1.

**Cách 1 — Logout FB + login lại**:
1. Mở tab mới → vào https://www.facebook.com/logout.php → confirm logout
2. Quay lại tool → bấm **➕ Thêm tài khoản FB**
3. Browser mở → trang Login FB → login tài khoản 2 → cấp quyền
4. ✅ Done

**Cách 2 — Chrome Incognito**:
1. Mở **Chrome → Ctrl+Shift+N** → cửa sổ Incognito
2. Vào https://www.facebook.com → login tài khoản 2 trong cửa sổ Incognito
3. Quay lại tool → bấm **➕ Thêm tài khoản FB** → browser default mở tab → có thể vẫn dùng session tài khoản 1
   - **Workaround**: copy URL OAuth từ console tool log → paste vào Incognito window đã login tài khoản 2
4. Cấp quyền → tool nhận token tài khoản 2

### Bước 4: Lặp cho tài khoản 3-10

Tổng setup ~15-20 phút. Sau khi xong, tab Tài khoản FB hiển thị 10 cards với tổng ~50 pages.

### Bước 5: Verify

1. Tab **📋 Fanpages** → thấy 50 pages, group theo tài khoản
2. Mỗi page có cột **Token** (masked) + **Active** ✅ + **Token expired** trống

---

## 8. Đăng bài đầu tiên

### Bước 1: Config Google Sheet

1. Tab **📊 Google Sheet**
2. Verify file credentials đã có (`✅ Đã có file credentials tại data/credentials.json`)
3. Sheet ID đã pre-fill từ `.env` → bấm **🔌 Test connection**
4. Phải hiện `✅ Kết nối OK — Sheet: ... / Tab: posts`
5. Bấm **💾 Lưu config**

### Bước 2: Thêm data mẫu vào Sheet

Mở Google Sheet → row 2, điền:

| A `video_link` | B `caption` | C `shopee_link` | D `comment_text` | E `used` | F `posted_at` | G `fb_post_ids` |
|---|---|---|---|---|---|---|
| `https://youtu.be/dQw4w9WgXcQ` | `Test bài đầu tiên 🚀` | `https://shopee.vn/test` | `Mua tại link bên dưới nha cả nhà` | (trống) | (trống) | (trống) |

### Bước 3: Test Dry Run trước (an toàn)

1. Tool tab **✏️ Tạo Bài** → bấm **🔄 Refresh Sheet** → bảng pending hiện row 2
2. Chọn **Row 2** từ dropdown
3. Form pre-fill 4 trường
4. Pages: chọn **"Chỉ 1 tài khoản"** + chọn 1 tài khoản test → multi-select tự fill 5 pages
5. **Bật 🧪 Dry Run** ✅
6. Chế độ: **⚡ Đăng ngay**
7. Bấm **🚀 Xác nhận**
8. Section Campaign #1 hiện ra → bật **Auto refresh 5s**
9. Banner step thay đổi: `🚀 Khởi động → 📦 Batch 1/1 → ⏸️ đợi delay → ... → ✅ Hoàn tất`
10. Tất cả 5 pages status `✅ Xong` (DRY mode)

### Bước 4: Đăng thật

1. Mở Sheet → cell E2 (cột used) → xóa nếu có giá trị
2. Tool → Refresh Sheet → chọn lại row 2
3. **TẮT 🧪 Dry Run** ❌
4. Multi-select chỉ **1 page test** đầu (an toàn)
5. **🚀 Xác nhận**
6. Đợi ~30s-1 phút → status `success`

### Bước 5: Verify

- ✅ Vào FB page → thấy bài + comment Shopee link
- ✅ Mở Sheet → row 2 cột E `TRUE`, cột F timestamp, cột G JSON
- ✅ Tool tab **📜 Lịch Sử** → bài có status `success`

### Bước 6: Scale lên nhiều page

Sau khi confirm 1 page OK:
1. Quay lại Sheet → reset row hoặc thêm row mới
2. Tool → multi-select **tất cả pages** (50 pages)
3. **🚀 Xác nhận**
4. Tool tự chia 5 batch × 10 page, delay 3-5 phút giữa batch
5. Tổng thời gian ~20 phút

---

## 9. Đặt lịch + tự động hóa

### Đặt lịch 1 bài

Tab Tạo Bài:
1. Chọn row Sheet
2. Chế độ: **⏰ Đặt lịch**
3. Pick ngày + giờ
4. **🚀 Xác nhận**
5. Sang tab **⏰ Lịch Đăng** → thấy bài đã đặt lịch

### Khi đến giờ

APScheduler tự trigger → bài đăng tự động.

⚠️ **Streamlit phải đang chạy** khi đến giờ. Tắt Streamlit → scheduler tắt → bài không đăng. Mở lại Streamlit trước giờ đăng → tool tự load lại lịch.

### Hủy lịch

Tab Lịch Đăng → nhập ID → **❌ Hủy lịch**.

---

## 10. Troubleshooting

### Lỗi: `Invalid Scopes: pages_read_user_content`

→ Quay lại Bước **3.3** add permission `pages_read_user_content` vào use case.

### Lỗi: `(#200) You do not have sufficient permissions`

→ Page Token thiếu quyền. Vào tab **Tài khoản FB** → bấm **🔑 Re-auth** ở account bị lỗi.

### Lỗi: `(#190) Error validating access token`

→ Token đã expire. Bấm **🔑 Re-auth** account đó.

### Tool báo failed nhưng bài đã lên FB

→ Có thể comment fail (Page Token thiếu `pages_manage_engagement`). Tool đã fix logic: post bài success vẫn coi là OK, chỉ ghi error_message ở comment.

### "Bạn hiện không xem được nội dung này" khi xem bằng account khác

→ Page mới tạo bị FB hạn chế tạm thời. Hoàn thiện thông tin page (avatar, ảnh bìa, about, category) + đợi 24-48h.

### Lỗi local server cổng 8765 đã bị dùng

→ Đổi `OAUTH_REDIRECT_PORT=8766` (hoặc khác) trong `.env` + update lại **URI chuyển hướng OAuth hợp lệ** trong FB App settings.

### Streamlit tắt giữa khi đăng

→ Job background bị mất. Quay lại tool → bài có thể ở status `running` mãi. Vào tab Lịch Sử → manually mark failed nếu cần. Sheet không bị update → có thể đăng lại.

### `Bad message format: Tried to use SessionInfo before it was initialized`

→ Bug Streamlit websocket. Bấm Ctrl+F5 để hard refresh. Không ảnh hưởng data.

---

## 11. (Optional) Deploy Cloudflare Worker

Khi bạn ship tool cho khách hàng, **không nên** để FB_APP_SECRET trong `.env` của khách (có thể bị decompile). Thay vào đó deploy backend Cloudflare Worker để giữ App Secret trên server.

### Deploy

1. Tạo account Cloudflare free: https://dash.cloudflare.com/sign-up
2. Vào **Workers & Pages → Create → Worker**
3. Mở file `cloudflare_worker.js` ở thư mục tool → copy nội dung → paste vào editor Worker
4. **Save & Deploy** → Worker có URL dạng `https://your-worker.your-subdomain.workers.dev`
5. Vào **Settings → Variables and Secrets** của Worker → thêm 2 secret:
   - `FB_APP_ID` = `<App ID>`
   - `FB_APP_SECRET` = `<App Secret>`
6. Save lại

### Update tool

Trong `.env`:
```env
FB_APP_ID=<App ID>
FB_APP_SECRET=
OAUTH_BACKEND_URL=https://your-worker.your-subdomain.workers.dev
```

→ Tool sẽ gọi Worker thay vì tự exchange với App Secret.
→ Khách cài tool **KHÔNG cần biết App Secret**.

### Free tier

- Cloudflare Workers free: 100K request/ngày
- Mỗi user OAuth ~1-2 request → đủ cho hàng nghìn user

---

## Checklist tổng

- [ ] Cài Python 3.11
- [ ] Tải tool, tạo venv, cài requirements
- [ ] Tạo FB App + add use case + add 5 permissions
- [ ] Setup Facebook Login for Business OAuth Settings
- [ ] Add `http://localhost:8765/callback` vào Valid OAuth Redirect URIs
- [ ] Lấy App ID + App Secret
- [ ] Add các tài khoản FB còn lại làm Tester (nếu Development mode)
- [ ] Tạo Google Cloud project + enable Sheets API + Drive API
- [ ] Tạo Service Account + tải `credentials.json` → `data/credentials.json`
- [ ] Tạo Google Sheet với 7 cột header → share cho service account email
- [ ] Cấu hình `.env` (FB_APP_ID, FB_APP_SECRET, GOOGLE_SHEET_ID)
- [ ] Chạy `streamlit run src/ui/app.py`
- [ ] Tab Tài khoản FB → Connect các tài khoản Facebook
- [ ] Tab Google Sheet → Test connection + Lưu config
- [ ] Thêm 1 row mẫu vào Sheet
- [ ] Tab Tạo Bài → Dry Run → Đăng thật 1 page
- [ ] Verify FB page + Sheet auto-update + Lịch Sử

---

## Tác giả

- Email: fbshopcloud@gmail.com
- Tool repo: (your-repo-url)
- Hỗ trợ: (your-discord/telegram)

---

> **Tài liệu này phiên bản v2.0** — sau khi tool hỗ trợ Local OAuth flow + Tab Tài khoản FB + Cloudflare Worker proxy. Ngày cập nhật: 2026-04-27.
