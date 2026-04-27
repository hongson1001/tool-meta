# CÀI ĐẶT TOOL CHO NGƯỜI NHÀ — Phiên bản đơn giản

> Tài liệu này dành cho kịch bản: **Bạn cài tool cho 1 người nhà dùng, bạn share toàn bộ resource có sẵn (App FB, Sheet, credentials.json)**. Không setup lại Google Cloud — tiết kiệm 15 phút.

## Tổng quan

Bạn ship cho người nhà:
- ✅ Tool ZIP (chứa code)
- ✅ File `credentials.json` (của bạn — đã có quyền truy cập Sheet)
- ✅ App ID + App Secret (của App "Auto Post Des" của bạn)
- ✅ Sheet ID (của Sheet bạn đang dùng, hoặc Sheet mới copy ra)

Người nhà chỉ:
- Cài Python 3.11
- Login Facebook (tài khoản FB của HỌ — để đăng lên page của họ)
- Dùng tool

**Tổng thời gian cài: ~20-25 phút** (đã skip Google Cloud setup).

---

## Chuẩn bị TRƯỚC khi đến máy người nhà (5 phút)

### A. Add người nhà làm Admin/Tester trên App FB

1. Vào: <https://developers.facebook.com/apps/809805552199715/roles/roles/>
2. Phần **"Quản trị viên"** (hoặc "Người dùng thử nghiệm") → **"+ Thêm"**
3. Nhập **Facebook ID** hoặc username của người nhà → Submit
4. Bảo người nhà mở: <https://www.facebook.com/settings?tab=apps_and_websites&section=tester_invitations>
5. Bấm **Accept** lời mời từ "Auto Post Des"

### B. Quyết định Sheet — 2 lựa chọn

#### Lựa chọn 1: Dùng LUÔN Sheet hiện tại của bạn (tiết kiệm nhất)
- Người nhà dùng cùng `GOOGLE_SHEET_ID` với bạn
- ⚠️ Nếu Sheet đã có data cũ (test bài đã đăng): mở Sheet → **xóa hết data từ row 2 trở xuống** (chỉ giữ header row 1)
- Sau khi xóa: Sheet sạch sẵn sàng cho người nhà nhập content mới

#### Lựa chọn 2: Tạo Sheet mới cho người nhà (an toàn hơn)
- Mở Sheet hiện tại của bạn → **File → Make a copy** → đặt tên `FB Content - <Tên người nhà>`
- Sheet mới có cấu trúc 7 cột header sẵn
- **Share Sheet mới cho email service account** (mở `credentials.json` → copy `client_email` → Share Sheet → Editor → Send)
- Lấy Sheet ID mới từ URL Sheet

→ Ghi nhớ Sheet ID dùng (lựa chọn 1 hoặc 2).

### C. Mang theo USB

- [ ] File ZIP: `fb-auto-post-v1.0-source.zip`
- [ ] File `credentials.json` của bạn (lấy từ `D:\Sơn\Sơn\private\fb-auto-post\data\credentials.json`)
- [ ] Đoạn config `.env` (soạn trong Notepad — xem mục D bên dưới)

### D. Soạn đoạn config `.env`

Mở Notepad, paste + điền giá trị:

```
FB_APP_ID=809805552199715
FB_APP_SECRET=<paste App Secret từ Dashboard FB của bạn>
FB_API_VERSION=v19.0

OAUTH_BACKEND_URL=
OAUTH_REDIRECT_PORT=8765

GOOGLE_CREDENTIALS_PATH=data/credentials.json
GOOGLE_SHEET_ID=<paste Sheet ID đã quyết định ở mục B>
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

→ Lấy App Secret tại: <https://developers.facebook.com/apps/809805552199715/settings/basic/> → Hiển thị → Copy

→ Save vào USB hoặc Notes của bạn.

---

## TẠI MÁY NGƯỜI NHÀ

## Bước 1 — Cài Python 3.11 (5 phút)

1. Mở browser, vào: <https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe>
2. Double-click file vừa tải
3. ⚠️ **TICK ô "Add python.exe to PATH"** ở màn hình đầu
4. Tick **"Install for all users"** → **Install Now** → đợi 2-3 phút
5. **Verify**: mở PowerShell mới → gõ `py -3.11 --version` → phải hiện `Python 3.11.9`

---

## Bước 2 — Giải nén ZIP (1 phút)

1. Tạo thư mục `C:\FBAutoPost`
2. Copy file ZIP từ USB vào `C:\FBAutoPost`
3. Right-click ZIP → **Extract All** → đường dẫn `C:\FBAutoPost`
4. Cấu trúc cuối: `C:\FBAutoPost\fb-auto-post\`

---

## Bước 3 — Copy `credentials.json` vào tool (30 giây)

1. Vào thư mục `C:\FBAutoPost\fb-auto-post\data\`
2. Copy file `credentials.json` từ USB vào đây
3. Đường dẫn cuối: `C:\FBAutoPost\fb-auto-post\data\credentials.json`

---

## Bước 4 — Tạo file `.env` (2 phút)

1. Vào `C:\FBAutoPost\fb-auto-post\`
2. Copy file `.env.example` → paste cùng thư mục → đổi tên thành `.env` (KHÔNG có chữ `.example`)
3. Right-click `.env` → **Open with → Notepad**
4. Xóa hết nội dung
5. Paste đoạn config bạn đã chuẩn bị (mục **D**)
6. **Ctrl+S** save → đóng Notepad

> Nếu Windows ẩn extension: View → tick **"File name extensions"** để thấy `.env` thay vì `env`.

---

## Bước 5 — Verify file đã đầy đủ

Kiểm tra:

- [x] `C:\FBAutoPost\fb-auto-post\.env`
- [x] `C:\FBAutoPost\fb-auto-post\data\credentials.json`
- [x] `C:\FBAutoPost\fb-auto-post\START.bat`
- [x] `C:\FBAutoPost\fb-auto-post\src\` (thư mục code)

---

## Bước 6 — Chạy tool lần đầu (5-7 phút cài thư viện)

1. Double-click **`START.bat`**
2. Cửa sổ Command Prompt đen mở ra
3. Tool tự cài venv + 16 thư viện (~3-5 phút lần đầu, tải ~300MB)
4. Browser tự mở `http://localhost:8501`
5. Lần đầu Streamlit hỏi email → bấm **Enter** bỏ qua

→ Sidebar có 7 tab: 👤 Tài khoản FB, 📋 Fanpages, 📊 Google Sheet, ✏️ Tạo Bài, ⏰ Lịch Đăng, 📜 Lịch Sử, ⚙️ Cài Đặt.

---

## Bước 7 — Connect tài khoản Facebook của người nhà (3 phút)

> **Quan trọng**: Đảm bảo browser đang login **TÀI KHOẢN FB CỦA NGƯỜI NHÀ** (không phải của bạn). Vào tab mới <https://www.facebook.com> để confirm.

1. Tab tool **👤 Tài khoản FB** → bấm **"➕ Thêm tài khoản FB"**
2. Browser tự mở tab mới → trang FB OAuth
3. Hiển thị: *"Auto Post Des đang yêu cầu quyền truy cập..."*
4. ⚠️ **Tick TẤT CẢ checkbox** → **Tiếp tục**
5. Màn **"Chọn các Trang để cấp quyền"** → chọn **"Tất cả các Trang hiện tại và sau này"** → **Tiếp tục**
6. Màn summary → **Lưu**
7. Browser hiện trang xanh "✅ Đã đăng nhập thành công" → đóng tab
8. Quay lại tool → toast `✅ Đã connect <Tên người nhà> (X pages)`

→ Card account hiện ra với danh sách pages của người nhà.

→ Tab **📋 Fanpages** sẽ thấy đủ X pages.

---

## Bước 8 — Verify Sheet trong tool (1 phút)

1. Tab **📊 Google Sheet**
2. File credentials phải hiện `✅ Đã có file credentials...`
3. Sheet ID đã pre-fill từ `.env`
4. Bấm **🔌 Test connection** → phải hiện `✅ Kết nối OK — Sheet: ...`
5. Bấm **💾 Lưu config**

---

## Bước 9 — Test đăng bài (5 phút)

### 9.1 Thêm row mẫu vào Sheet

Mở Sheet trên browser → row 2:

| A `video_link` | B `caption` | C `shopee_link` | D `comment_text` | E F G |
|---|---|---|---|---|
| `https://youtu.be/dQw4w9WgXcQ` | `Test bài đầu tiên` | `https://shopee.vn/test` | `Mua tại link bên dưới` | (trống) |

### 9.2 Đăng qua tool

1. Tab **✏️ Tạo Bài** → bấm **🔄 Refresh Sheet** → row 2 xuất hiện trong pending
2. Chọn **Row 2** từ dropdown
3. Form pre-fill 4 trường
4. Pages: chọn **Tất cả** hoặc **Chỉ 1 tài khoản** → 1 page test
5. Variant ON, **TẮT 🧪 Dry Run**, **⚡ Đăng ngay**
6. Bấm **🚀 Xác nhận**
7. Bật toggle **Auto refresh 5s**
8. Đợi ~30-60s → status `success` ✅

### 9.3 Verify

- ✅ Vào FB page của người nhà → thấy bài + comment Shopee
- ✅ Mở Sheet → row 2 cột E `TRUE`, F timestamp, G JSON

---

## Bước 10 — Hướng dẫn người nhà dùng hằng ngày (5 phút training)

### 10.1 Tạo shortcut Desktop

1. Right-click `C:\FBAutoPost\fb-auto-post\START.bat`
2. **Send to → Desktop (create shortcut)**
3. Đổi tên shortcut thành "FB Auto Post"

### 10.2 Hướng dẫn người nhà

> "Mỗi ngày anh/chị làm theo 4 bước:"

1. **Mở Google Sheet** (link đã đặt favorite trên browser) → thêm row mới với content:
   - Cột A: link YouTube (KHÔNG phải TikTok — TikTok không hiện video inline)
   - Cột B: caption bài đăng
   - Cột C: link Shopee
   - Cột D: text comment
   - Cột E, F, G: **để trống** (tool tự fill)

2. **Double-click "FB Auto Post"** trên Desktop → tool mở browser

3. **Tab Tạo Bài**:
   - Bấm **🔄 Refresh Sheet**
   - Chọn row vừa thêm
   - Multi-select tất cả pages (hoặc chọn 1 nhóm)
   - Bấm **🚀 Xác nhận**
   - Đợi tool đăng (xem toast notification)

4. **Đóng tool** khi xong: đóng cửa sổ Command Prompt đen

### 10.3 Lưu ý quan trọng nói với người nhà

- ✅ **Chỉ dùng link YouTube** trong cột video_link (FB hiện video play inline). TikTok thì không.
- ✅ **Mỗi row 1 sản phẩm** — comment Shopee phải khớp đúng sản phẩm trong caption
- ⚠️ **Đừng đăng nhanh quá** — tool có giới hạn batch 10 page, delay 3-5 phút giữa batch (tránh FB flag)
- ⚠️ **Đừng share file `.env` và `credentials.json`** cho ai
- 🔧 **Khi gặp lỗi** → screenshot + báo bạn (Zalo)

---

## Bước 11 — Backup trước khi bạn rời

1. Tab **⚙️ Cài Đặt** → bấm **💾 Backup ngay** (tạo `posts.db` backup đầu tiên)
2. Hướng dẫn người nhà bấm Backup hằng tuần
3. Backup files lưu ở `C:\FBAutoPost\fb-auto-post\backups\`

---

## Checklist cuối — Trước khi bạn rời máy người nhà

- [ ] Tool chạy được `START.bat` mà không lỗi
- [ ] Tab Tài khoản FB hiển thị tài khoản của người nhà (không phải của bạn)
- [ ] Tab Fanpages hiển thị đủ pages của người nhà
- [ ] Đăng test 1 bài thật → success → bài + comment lên FB
- [ ] Sheet auto-update sau đăng (cột E/F/G)
- [ ] Tạo shortcut Desktop
- [ ] Người nhà đã hiểu cách thêm row vào Sheet + bấm đăng
- [ ] Đã share Zalo support cho người nhà
- [ ] Lưu lại screenshot tab Tài khoản FB + Sheet ID dùng (để debug từ xa nếu cần)

---

## Lỗi thường gặp + Fix nhanh

### `py không được nhận diện`
→ Cài lại Python, tick "Add to PATH"

### Tool báo `Chưa cấu hình FB_APP_ID`
→ File `.env` chưa có hoặc sai. Kiểm tra `C:\FBAutoPost\fb-auto-post\.env`

### Tool báo `Chưa upload credentials.json`
→ File `credentials.json` chưa ở `data/`. Copy lại từ USB

### Bấm "Thêm tài khoản FB" → FB báo `App not active`
→ Người nhà chưa Accept Tester invite. Quay lại mục **A** ở đầu tài liệu, gửi link Accept

### Connect FB xong nhưng `0 pages`
→ Tài khoản FB người nhà không là Admin của page nào. Hướng dẫn họ tạo page test:
- Vào <https://www.facebook.com/pages/create/> → tạo 1 page bất kỳ
- Quay lại tool → tab Tài khoản FB → bấm **🔄 Refresh pages**

### Đăng bài thành công nhưng không thấy trên FB (chỉ admin xem được)
→ Page mới tạo bị FB hạn chế tạm thời. Người nhà hoàn thiện thông tin page (avatar, ảnh bìa, about) + đợi 24-48h.

### `Bad message format: Tried to use SessionInfo before initialized`
→ Bug Streamlit websocket. Bấm **Ctrl+F5** hard refresh browser.

---

## Update tool sau này

Khi bạn fix bug / thêm tính năng:

### Phía bạn

1. Code update → test trên máy bạn
2. Re-zip:
   ```powershell
   cd D:\Sơn\Sơn\private\_ship
   Remove-Item -Recurse fb-auto-post -ErrorAction SilentlyContinue
   xcopy /E /I /Y D:\Sơn\Sơn\private\fb-auto-post\src .\fb-auto-post\src
   xcopy /Y D:\Sơn\Sơn\private\fb-auto-post\*.bat .\fb-auto-post\
   xcopy /Y D:\Sơn\Sơn\private\fb-auto-post\*.md .\fb-auto-post\
   xcopy /Y D:\Sơn\Sơn\private\fb-auto-post\requirements.txt .\fb-auto-post\
   xcopy /Y D:\Sơn\Sơn\private\fb-auto-post\.env.example .\fb-auto-post\
   xcopy /Y D:\Sơn\Sơn\private\fb-auto-post\.gitignore .\fb-auto-post\
   xcopy /Y D:\Sơn\Sơn\private\fb-auto-post\cloudflare_worker.js .\fb-auto-post\
   powershell Compress-Archive -Path 'fb-auto-post' -DestinationPath 'fb-auto-post-v1.X.zip' -Force
   ```
3. Gửi ZIP mới qua Zalo

### Phía người nhà

1. Đóng tool
2. Tải ZIP mới
3. Giải nén → **chỉ ghi đè thư mục `src/`** (không động `.env`, `data/`, `venv/`)
4. Chạy lại `START.bat`

→ Code mới + data cũ vẫn còn.

---

## Tổng thời gian setup

| Bước | Thời gian |
|---|---|
| Add Admin/Tester trên FB App + người nhà Accept | 2 phút |
| Cài Python 3.11 | 5 phút |
| Giải nén ZIP + Copy credentials.json | 2 phút |
| Tạo `.env` | 2 phút |
| Chạy START.bat lần đầu | 5-7 phút |
| Connect tài khoản FB | 3 phút |
| Verify Sheet + Test đăng bài | 5 phút |
| Hướng dẫn người nhà | 5 phút |
| **TỔNG** | **~25-30 phút** |

→ Đã skip Google Cloud setup (10-12 phút) so với phiên bản đầy đủ.

---

## Nếu sau này có khách hàng KHÔNG phải người nhà

→ Tham khảo file `CAI_DAT_MAY_KHACH.md` (phiên bản đầy đủ) — bao gồm setup Google Cloud riêng cho mỗi khách (an toàn hơn).

---

## Liên lạc

- **Người nhà gặp lỗi** → screenshot gửi bạn qua Zalo
- **Bạn cần fix từ xa** → cài TeamViewer/AnyDesk: <https://www.teamviewer.com/vi/download/windows/>

---

> **Phiên bản**: v1.0 — 2026-04-27. Tài liệu rút gọn cho kịch bản single-user (1 người nhà dùng).
