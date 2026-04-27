# CÀI ĐẶT TOOL TRÊN MÁY NGƯỜI DÙNG

> **Tài liệu này dành cho bạn (người ship tool)** khi cài tool lên máy của người nhà / khách hàng. Theo từng bước để cài xong trong **~30-45 phút**.

## Chuẩn bị TRƯỚC khi đến máy người nhà

### A. Mang theo (USB/Drive/cloud)

- [ ] File ZIP: `fb-auto-post-v1.0-source.zip` (`D:\Sơn\Sơn\private\_ship\`)
- [ ] Tài liệu này (`CAI_DAT_MAY_KHACH.md`)
- [ ] Đoạn config `.env` đã có App ID + App Secret của bạn (sẽ paste sau)

### B. Lấy thông tin của người nhà

- [ ] **Facebook ID** hoặc username (lấy từ profile FB của họ)
- [ ] **Email Gmail** của họ (để đăng ký Google Cloud)
- [ ] **Tên + danh sách Fanpage** họ quản lý (để verify sau khi connect)

### C. Add người nhà làm Tester (hoặc Admin) trên FB App của bạn

> **Lưu ý**: Bạn đã chọn cho Admin. OK, vẫn dùng được. Nhưng tip: nếu sau này có thêm khách lạ, dùng role **Tester** thay vì Admin.

1. Vào: <https://developers.facebook.com/apps/809805552199715/roles/roles/>
2. Phần **"Quản trị viên"** (Admins) → bấm **"+ Thêm quản trị viên"**
3. Nhập **Facebook ID** hoặc username của người nhà → Submit
4. Bảo người nhà mở: <https://www.facebook.com/settings?tab=apps_and_websites&section=tester_invitations>
5. Bấm **Accept** lời mời từ "Auto Post Des"

→ Confirm họ đã Accept (xem checkbox xanh trong Dashboard App).

### D. Soạn sẵn đoạn config `.env`

Mở Notepad, soạn đoạn này (paste sau khi cài máy):

```
FB_APP_ID=809805552199715
FB_APP_SECRET=<paste App Secret từ Dashboard FB của bạn>
FB_API_VERSION=v19.0

OAUTH_BACKEND_URL=
OAUTH_REDIRECT_PORT=8765

GOOGLE_CREDENTIALS_PATH=data/credentials.json
GOOGLE_SHEET_ID=
GOOGLE_SHEET_TAB=posts

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

→ Lấy App Secret tại: <https://developers.facebook.com/apps/809805552199715/settings/basic/> → **Hiển thị**

→ Save vào USB hoặc copy sẵn vào clipboard.

---

## Bước 1 — Cài Python 3.11 (5 phút)

### 1.1 Mở browser trên máy người nhà

Vào: <https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe>

→ File `python-3.11.9-amd64.exe` (~25MB) tự download.

### 1.2 Cài đặt

1. Double-click file vừa tải
2. ⚠️ **TICK ô "Add python.exe to PATH"** ở màn hình đầu (cực kỳ quan trọng)
3. Tick **"Install for all users"**
4. Bấm **"Install Now"** → đợi 2-3 phút
5. Khi hiện *"Setup was successful"* → bấm **Close**

### 1.3 Verify

Mở **PowerShell** mới (Start → gõ `powershell` → Enter), gõ:

```powershell
py -3.11 --version
```

Phải hiện `Python 3.11.9`.

> ❌ Nếu báo `not recognized` → cài lại Python, đảm bảo tick "Add to PATH".

---

## Bước 2 — Giải nén ZIP (1 phút)

### 2.1 Tạo thư mục

Tạo thư mục: `C:\FBAutoPost`

⚠️ Đường dẫn **KHÔNG** có dấu/tiếng Việt/khoảng trắng (vd: tránh `D:\Tài liệu\Tool FB`).

### 2.2 Copy file ZIP

Copy `fb-auto-post-v1.0-source.zip` từ USB vào `C:\FBAutoPost\`.

### 2.3 Giải nén

1. Right-click file ZIP → **"Extract All..."**
2. Đường dẫn đích: `C:\FBAutoPost`
3. Bấm **Extract**

→ Cấu trúc cuối: `C:\FBAutoPost\fb-auto-post\` chứa `src/`, `START.bat`, `.env.example`, etc.

---

## Bước 3 — Setup Google Cloud + Sheet (10 phút)

> **Người nhà có sẵn tài khoản Gmail**? Nếu chưa, tạo Gmail mới trước.

### 3.1 Tạo Google Cloud Project

1. Login Gmail của người nhà trên browser
2. Vào: <https://console.cloud.google.com/projectcreate>
3. **Project name**: `FB Post Tool`
4. **Organization**: chọn **"No organization"** ⚠️ (quan trọng — tránh policy block)
5. Bấm **Create** → đợi ~30s

### 3.2 Bật 2 APIs

Mở 2 link, ở mỗi link bấm **"Enable"**:
- <https://console.cloud.google.com/apis/library/sheets.googleapis.com>
- <https://console.cloud.google.com/apis/library/drive.googleapis.com>

→ Đảm bảo header trên cùng đang ở project `FB Post Tool`.

### 3.3 Tạo Service Account

1. Vào: <https://console.cloud.google.com/iam-admin/serviceaccounts>
2. **+ Create Service Account**
3. **Name**: `fb-auto-post-bot`
4. **Service account ID**: tự fill → **Create and Continue**
5. **Grant access**: để trống → **Continue**
6. **Grant users access**: để trống → **Done**

### 3.4 Tạo JSON Key

1. Click vào service account vừa tạo
2. Tab **"Keys"** → **"Add Key" → "Create new key"**
3. Chọn **JSON** → **Create**
4. File `xxx.json` tự download → đổi tên thành **`credentials.json`**
5. Copy `credentials.json` vào: `C:\FBAutoPost\fb-auto-post\data\`

### 3.5 Tạo Google Sheet

1. Vào: <https://sheets.new>
2. Tên: `FB Content Queue`
3. Tab đầu tiên (Sheet1) → right-click → Rename → đổi thành `posts`
4. Hàng 1 — gõ 7 cột header **CHÍNH XÁC**:

   | A | B | C | D | E | F | G |
   |---|---|---|---|---|---|---|
   | `video_link` | `caption` | `shopee_link` | `comment_text` | `used` | `posted_at` | `fb_post_ids` |

### 3.6 Share Sheet cho Service Account

1. Mở `credentials.json` bằng Notepad
2. Tìm dòng `"client_email": "fb-auto-post-bot@xxx.iam.gserviceaccount.com"` → copy email
3. Vào Google Sheet → bấm **Share** (góc phải trên)
4. Paste email service account → quyền **Editor** → bỏ tick "Notify people" → **Send**
5. Nếu Google warning *"This email isn't a Google Account"* → bấm **"Share anyway"**

### 3.7 Lấy Sheet ID

URL Sheet:
```
https://docs.google.com/spreadsheets/d/SHEET_ID_NAY/edit
```

Copy đoạn `SHEET_ID_NAY` (giữa `/d/` và `/edit`) → lưu Notepad tạm.

---

## Bước 4 — Tạo file `.env` (3 phút)

### 4.1 Copy template

Vào `C:\FBAutoPost\fb-auto-post\`:
- Copy file `.env.example`
- Paste cùng thư mục → đổi tên thành `.env` (KHÔNG có chữ `.example`)

> Windows có thể ẩn extension. Nếu không thấy `.env`, vào View → tick **"File name extensions"**.

### 4.2 Mở `.env` bằng Notepad

Right-click `.env` → **Open with → Notepad**.

### 4.3 Paste config bạn đã chuẩn bị

Xóa hết nội dung trong file `.env`, paste đoạn config đã soạn (mục **D** ở đầu tài liệu).

### 4.4 Điền Sheet ID

Tìm dòng:
```
GOOGLE_SHEET_ID=
```
Paste Sheet ID lấy từ Bước 3.7 vào sau dấu `=`:
```
GOOGLE_SHEET_ID=1tQeUewxznI0JdgPGRh9tLTsXS7KvVHW_3U2x5SVlQgc
```

### 4.5 Save

**Ctrl+S** → đóng Notepad.

---

## Bước 5 — Verify file đã đầy đủ

Kiểm tra cấu trúc `C:\FBAutoPost\fb-auto-post\`:

- [x] `.env` (vừa tạo, có App ID + Secret + Sheet ID)
- [x] `data\credentials.json` (vừa copy từ Google Cloud)
- [x] `START.bat`
- [x] `requirements.txt`
- [x] `src\` (thư mục code)

Nếu thiếu file nào → kiểm tra lại bước trước đó.

---

## Bước 6 — Chạy tool lần đầu (5-7 phút cài venv)

### 6.1 Double-click `START.bat`

Cửa sổ Command Prompt đen mở ra:

```
================================================
   FB AUTO POST TOOL
================================================

[SETUP] Lan dau chay - dang cai dat moi truong...
[SETUP] Dang cai thu vien (mat 3-5 phut)...
```

→ Tool tự:
1. Tạo virtual environment (`venv\`)
2. Cài 16 thư viện qua pip (~3-5 phút lần đầu, tải ~300MB)
3. Khởi động Streamlit

### 6.2 Browser tự mở

Sau ~5 phút, browser tự mở `http://localhost:8501` với giao diện tool.

→ Lần đầu Streamlit hỏi email — bấm **Enter** để bỏ qua.

### 6.3 Verify giao diện

Sidebar trái phải có 7 tab:
- 👤 Tài khoản FB
- 📋 Fanpages
- 📊 Google Sheet
- ✏️ Tạo Bài
- ⏰ Lịch Đăng
- 📜 Lịch Sử
- ⚙️ Cài Đặt

→ Default ở tab **Tài khoản FB** với thông báo "Chưa có tài khoản nào".

---

## Bước 7 — Connect tài khoản Facebook (5 phút)

### 7.1 Đảm bảo người nhà đang login FB trên browser

→ Mở tab mới <https://www.facebook.com> → confirm đã login.

### 7.2 Bấm "+ Thêm tài khoản FB" trên tool

Tab **Tài khoản FB** → bấm nút xanh **"➕ Thêm tài khoản FB"**.

### 7.3 Cấp quyền

- Browser tự mở tab mới → trang FB OAuth
- Hiển thị: *"Auto Post Des đang yêu cầu quyền truy cập..."*
- ⚠️ **Tick TẤT CẢ checkbox**:
  - Tạo và quản lý nội dung trên Trang
  - Đọc nội dung đã đăng lên Trang
  - Hiển thị danh sách Trang bạn quản lý
  - (và các quyền khác hiện ra)
- Bấm **Tiếp tục**

→ Có thể hiện màn **"Chọn các Trang để cấp quyền"**:
- Chọn **"Tất cả các Trang hiện tại và sau này"**
- Bấm **Tiếp tục**

→ Màn summary cuối → bấm **Lưu** / **Xong**

### 7.4 Browser hiện trang xanh thành công

```
✅ Đã đăng nhập thành công!
Bạn có thể đóng tab này và quay lại tool FB Auto Post.
```

→ Đóng tab này.

### 7.5 Quay lại tool

Tab tool có toast xanh:
```
✅ Đã connect <Tên người nhà> (X pages, long-lived 60 ngày)
```

→ Card account hiện ra với danh sách pages của họ.

### 7.6 Verify

Sang tab **📋 Fanpages → 📑 Danh sách**:
- Phải thấy đủ X pages của người nhà
- Mỗi page có cột **Tài khoản** = tên người nhà
- Token ✅ Active

---

## Bước 8 — Config Google Sheet + Test đăng bài (5 phút)

### 8.1 Setup Sheet trong tool

Tab **📊 Google Sheet**:
- File credentials: phải hiện `✅ Đã có file credentials tại data/credentials.json`
- Sheet ID: pre-fill từ `.env`
- Tab name: `posts`
- Bấm **🔌 Test connection** → phải hiện `✅ Kết nối OK`
- Bấm **💾 Lưu config**

### 8.2 Thêm row mẫu vào Sheet

Mở Google Sheet trên browser, hàng 2:

| A `video_link` | B `caption` | C `shopee_link` | D `comment_text` | E F G |
|---|---|---|---|---|
| `https://youtu.be/dQw4w9WgXcQ` | `Test bài đầu tiên` | `https://shopee.vn/test` | `Mua tại link bên dưới` | (trống) |

### 8.3 Đăng bài thử

Tab **✏️ Tạo Bài**:
1. Bấm **🔄 Refresh Sheet** → row 2 hiện trong pending
2. Chọn **Row 2** từ dropdown
3. Form pre-fill 4 trường
4. Pages: **Tất cả** hoặc **Chỉ 1 tài khoản** (chọn 1 page test trước)
5. Variant ON, **TẮT 🧪 Dry Run**, **⚡ Đăng ngay**
6. Bấm **🚀 Xác nhận**
7. Section Campaign #1 hiện ra → bật **Auto refresh 5s**
8. Đợi ~30-60s → status `success` ✅

### 8.4 Verify trên FB Page

Mở FB page → phải thấy:
- ✅ Bài mới với caption variant + link YouTube
- ✅ Comment đầu tiên có Shopee link

### 8.5 Verify Google Sheet

Mở Sheet → row 2:
- ✅ Cột E `used` = `TRUE`
- ✅ Cột F `posted_at` = timestamp
- ✅ Cột G `fb_post_ids` = JSON

---

## Bước 9 — Hướng dẫn người nhà dùng hằng ngày

### 9.1 Cách dùng tool mỗi ngày

1. **Mở Google Sheet** → thêm row mới (4 cột đầu, để trống E/F/G)
2. **Double-click `START.bat`** trên Desktop hoặc `C:\FBAutoPost\fb-auto-post\`
3. Browser tự mở tool
4. Tab **Tạo Bài** → **Refresh Sheet** → chọn row → **🚀 Xác nhận**
5. Đợi tool đăng xong (xem toast notification)
6. Vào FB page xem bài + comment
7. Đóng tool: đóng cửa sổ Command Prompt đen

### 9.2 Tạo shortcut Desktop cho `START.bat` (tiện hơn)

1. Right-click `C:\FBAutoPost\fb-auto-post\START.bat`
2. **Send to → Desktop (create shortcut)**
3. Trên Desktop → right-click shortcut → Rename → đổi thành "FB Auto Post"
4. Right-click shortcut → Properties → Change Icon → chọn icon đẹp (optional)

### 9.3 Hướng dẫn nâng cao (nếu cần)

- **Đặt lịch đăng**: Tab Tạo Bài → chế độ **⏰ Đặt lịch** → chọn ngày/giờ
- **Xem lịch sử**: Tab **📜 Lịch Sử** → Dashboard + filter
- **Connect thêm tài khoản FB**: Tab Tài khoản FB → **+ Thêm tài khoản** (logout FB cũ trước)

---

## Bước 10 — Backup quan trọng

### 10.1 Hướng dẫn người nhà backup

Tab **⚙️ Cài Đặt** → bấm **💾 Backup ngay** mỗi tuần.

→ Backup file `posts.db` lưu vào `C:\FBAutoPost\fb-auto-post\backups\`.

→ Nếu DB hỏng → Restore từ file backup gần nhất.

### 10.2 Bạn (người ship) lưu lại:

- [ ] Screenshot tab Tài khoản FB sau setup (để khi support biết người nhà có bao nhiêu account/page)
- [ ] App ID + App Secret (đã có)
- [ ] Sheet ID của người nhà (để debug từ xa nếu cần)

---

## Troubleshooting — Lỗi thường gặp

### ❌ `py không được nhận diện` khi chạy START.bat

→ Python chưa cài hoặc chưa add vào PATH.
**Fix**: Cài lại Python 3.11, tick **"Add to PATH"** ở màn hình đầu.

### ❌ START.bat đóng ngay sau khi mở

→ Có lỗi khi cài thư viện. Mở PowerShell thủ công để xem lỗi:
```powershell
cd C:\FBAutoPost\fb-auto-post
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
→ Đọc lỗi cụ thể.

### ❌ Tool báo `Chưa cấu hình FB_APP_ID`

→ File `.env` chưa được tạo/điền. Quay lại **Bước 4**.

### ❌ Tool báo `Chưa upload credentials.json`

→ File `credentials.json` chưa ở `C:\FBAutoPost\fb-auto-post\data\`. Quay lại **Bước 3.4**.

### ❌ Bấm "Thêm tài khoản FB" → browser mở nhưng FB báo lỗi `Invalid App`

→ Người nhà chưa accept Tester invite. Quay lại mục **C** ở đầu tài liệu.

### ❌ Connect tài khoản FB xong nhưng không thấy page nào

→ Tài khoản FB của người nhà không quản lý fanpage nào. Tạo 1 page test:
- Vào <https://www.facebook.com/pages/create/> → tạo 1 page bất kỳ
- Quay lại tool → Tab Tài khoản FB → bấm **🔄 Refresh pages** ở card account

### ❌ Đăng bài success nhưng không thấy trên FB

→ Page mới tạo bị FB hạn chế tạm thời. Hoàn thiện thông tin page (avatar, cover, about) + đợi 24-48h.

### ❌ `Bad message format: Tried to use SessionInfo before initialized`

→ Bug Streamlit websocket. **Ctrl+F5** hard refresh browser.

### ❌ Tool không update khi push code mới

→ Sau khi nhận file ZIP mới từ bạn:
1. Đóng tool (đóng Command Prompt)
2. Giải nén ZIP mới → ghi đè thư mục `src/`
3. Chạy lại `START.bat`

### ❌ Cổng 8765 đã bị app khác dùng

→ Đổi `OAUTH_REDIRECT_PORT=8766` trong `.env` + thêm `http://localhost:8766/callback` vào FB App OAuth Redirect URIs.

---

## Update tool sau này

Khi bạn fix bug / thêm tính năng:

### Phía bạn:

1. Update code trong `D:\Sơn\Sơn\private\fb-auto-post\`
2. Test trên máy bạn
3. Re-zip:
   ```powershell
   cd D:\Sơn\Sơn\private\_ship
   Remove-Item -Recurse fb-auto-post -ErrorAction SilentlyContinue
   xcopy /E /I /Y D:\Sơn\Sơn\private\fb-auto-post\src .\fb-auto-post\src
   xcopy /E /I /Y D:\Sơn\Sơn\private\fb-auto-post\*.bat .\fb-auto-post\
   xcopy /E /I /Y D:\Sơn\Sơn\private\fb-auto-post\*.md .\fb-auto-post\
   xcopy /Y D:\Sơn\Sơn\private\fb-auto-post\requirements.txt .\fb-auto-post\
   xcopy /Y D:\Sơn\Sơn\private\fb-auto-post\.env.example .\fb-auto-post\
   xcopy /Y D:\Sơn\Sơn\private\fb-auto-post\.gitignore .\fb-auto-post\
   xcopy /Y D:\Sơn\Sơn\private\fb-auto-post\cloudflare_worker.js .\fb-auto-post\
   powershell Compress-Archive -Path 'fb-auto-post' -DestinationPath 'fb-auto-post-v1.X-source.zip' -Force
   ```
4. Gửi file ZIP mới qua Zalo/Drive

### Phía người nhà:

1. Đóng tool
2. Tải ZIP mới về
3. Giải nén → **chỉ ghi đè thư mục `src/`** (không động `.env`, `data/`, `venv/`, `logs/`)
4. Chạy lại `START.bat`

→ Tool có code mới, data cũ vẫn còn (DB + credentials + .env).

---

## Checklist cuối — Trước khi rời máy người nhà

- [ ] Tool chạy được `START.bat` thành công
- [ ] Tab Tài khoản FB hiển thị đủ accounts của người nhà
- [ ] Tab Fanpages hiển thị đủ pages
- [ ] Đăng test 1 bài thật → success → bài + comment lên FB OK
- [ ] Sheet auto-update sau khi đăng (cột E/F/G)
- [ ] Tạo shortcut Desktop cho `START.bat`
- [ ] Hướng dẫn người nhà dùng hằng ngày (5 phút training)
- [ ] Lưu lại thông tin người nhà (FB ID, Sheet ID, số account/page)
- [ ] Nhắc người nhà:
  - [ ] Backup DB hằng tuần (tab Cài Đặt → Backup ngay)
  - [ ] Đừng chia sẻ file `.env` và `credentials.json`
  - [ ] Khi gặp lỗi → screenshot + báo bạn ngay

---

## Liên lạc support

- **Người nhà gặp lỗi** → screenshot gửi bạn qua Zalo
- **Bạn xa, cần fix** → TeamViewer / AnyDesk:
  - Tải TeamViewer free: <https://www.teamviewer.com/vi/download/windows/>
  - Hướng dẫn người nhà cài + share ID/Password
  - Bạn vào fix từ xa

---

## Tổng thời gian setup

| Bước | Thời gian |
|---|---|
| Add Tester/Admin trên FB App + người nhà Accept | 2 phút |
| Cài Python 3.11 | 5 phút |
| Giải nén ZIP | 1 phút |
| Setup Google Cloud + Sheet | 10-12 phút |
| Tạo `.env` | 3 phút |
| Chạy START.bat lần đầu (cài thư viện) | 5-7 phút |
| Connect tài khoản FB + verify | 5 phút |
| Test đăng bài | 5 phút |
| Hướng dẫn người nhà dùng | 5 phút |
| **TỔNG** | **~40-50 phút** |

→ Lần thứ 2 trở đi (đã có Python + ZIP), chỉ ~20-30 phút.

---

> **Tài liệu này phiên bản v1.0** — cập nhật ngày 2026-04-27.
> Gặp vấn đề chưa có trong tài liệu? Tham khảo `SETUP.md` (chi tiết hơn) hoặc liên hệ trực tiếp.
