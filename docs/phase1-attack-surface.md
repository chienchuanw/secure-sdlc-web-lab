# Phase 1：功能設計與攻擊面建模

> 目標：在寫程式碼之前，識別所有潛在攻擊面

## 應用程式類型

**部落格/論壇系統**

---

## 功能模組清單

### 1. 使用者認證與授權模組

**功能描述**：

- 使用者註冊
- 登入/登出
- 密碼重設
- 記住我功能

**輸入點（User Input）**：

- [ ] 註冊表單：username, email, password, password_confirm
- [ ] 登入表單：username/email, password, remember_me (checkbox)
- [ ] 密碼重設：email, new_password, reset_token (URL parameter)

**身份/權限邊界**：

- [ ] 匿名使用者 → 已登入使用者
- [ ] Session 管理（何時建立、何時失效）
- [ ] "記住我" token 的安全性

**與外部系統的互動**：

- [ ] Email 發送服務（密碼重設信件）
- [ ] Session store（Redis 或 Database）

**潛在攻擊面**：

- [ ] 弱密碼（密碼複雜度要求）
- [ ] 使用者名稱列舉（註冊/登入錯誤訊息洩漏帳號存在與否）
- [ ] Session Fixation
- [ ] CSRF on login/logout
- [ ] Timing attack（登入回應時間差異）
- [ ] 暴力破解（無 rate limiting）
- [ ] Password reset token 可預測
- [ ] Remember me token 未加密或可重放

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

## 下一步（進入 Phase 2）

當你能夠清楚回答以下問題時，Phase 1 就完成了：

1. ✅ 系統有哪些輸入點？
2. ✅ 哪些地方需要檢查權限？
3. ✅ 哪些資料不應該信任使用者？
4. ✅ 有哪些隱藏的 admin 或 internal endpoints？
5. ✅ 每個功能最可能出現什麼漏洞？

**準備好進入 Phase 2 時**，我們將開始實作這些功能，並**刻意**引入特定漏洞供後續學習修復。
