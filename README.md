# Secure SDLC Web Lab

一個用於學習和實踐 Secure Software Development Lifecycle (SDLC) 的漏洞實驗環境。

## Phase 0：技術選型與安全邊界定義

### 技術選型

| 項目                  | 技術           | 原因                                                            |
| --------------------- | -------------- | --------------------------------------------------------------- |
| **Backend Framework** | Django 6.x     | 成熟的 Python Web 框架，內建多項安全功能（CSRF、XSS 防護、ORM） |
| **Database**          | PostgreSQL 16  | 企業級關聯式資料庫，支援進階安全功能                            |
| **Authentication**    | Session-based  | Django 內建 session 機制，server-side 管理，安全性較容易控制    |
| **Deployment**        | Docker Compose | 標準化開發環境，確保一致性與可重現性                            |
| **Language**          | Python 3.12+   | 現代 Python 版本，支援最新安全特性                              |

### Scope Definition

#### ✅ In Scope（測試範圍內）

本專案**刻意設計**以下漏洞，供學習和實踐防禦措施：

**Web Application Security**

- SQL Injection (SQLi)
- Cross-Site Scripting (XSS)
- Cross-Site Request Forgery (CSRF)
- Insecure Direct Object References (IDOR)
- Authentication & Session Management flaws
- Authorization & Access Control issues
- Server-Side Request Forgery (SSRF)
- XML External Entity (XXE) attacks
- Insecure Deserialization
- Security Misconfiguration

**API Security**

- Broken Object Level Authorization
- Broken Authentication
- Excessive Data Exposure
- Mass Assignment
- Security Misconfiguration

**Business Logic**

- Race Conditions
- Price Manipulation
- Privilege Escalation
- Workflow Bypass

#### ❌ Out of Scope（測試範圍外）

以下攻擊類型**刻意不處理**，原因如下：

| 攻擊類型                 | 不處理原因                                                            |
| ------------------------ | --------------------------------------------------------------------- |
| **DoS/DDoS 攻擊**        | 需要基礎設施層級的防護（WAF、CDN、Rate Limiting），超出應用層安全範疇 |
| **實體社交工程**         | 屬於人員安全訓練範疇，非軟體開發可控                                  |
| **進階持續性威脅 (APT)** | 需要完整 SOC/SIEM 系統，超出單一應用程式範圍                          |
| **零日漏洞利用**         | 需要持續追蹤 CVE 與套件更新，屬於維運範疇                             |
| **實體硬體攻擊**         | Side-channel attacks、硬體木馬等需要硬體安全專業                      |
| **網路層攻擊**           | TCP/IP layer attacks、ARP spoofing 等屬於網路安全範疇                 |
| **供應鏈攻擊**           | 依賴套件的惡意程式碼注入，需要額外的 SCA 工具                         |

### 一句話總結

> **這個專案專注於應用層的程式碼安全漏洞，不處理基礎設施、網路層、實體層以及需要組織級資源的攻擊類型。**

原因：本專案目標是教育開發者如何在**程式碼層級**實踐 Secure SDLC，而非建置完整的企業級安全架構。

---

## 快速開始

### 前置需求

- Docker & Docker Compose
- Python 3.12+

### 啟動環境

```bash
# 複製環境變數範本
cp .env.template .env

# 啟動 Docker 容器
docker-compose up -d

# 檢查服務狀態
docker-compose ps
```

應用程式將運行在 `http://localhost:8000`

### 停止環境

```bash
docker-compose down

# 若要清除資料庫資料
docker-compose down -v
```

---

## 專案結構

```
secure-sdlc-web-lab/
├── core/                          # Django 核心設定
├── docs/                          # 文件
│   └── phase1-attack-surface.md  # Phase 1 攻擊面分析
├── .env                          # 環境變數（不納入版控）
├── .env.template                 # 環境變數範本
├── docker-compose.yml            # Docker 編排設定
├── Dockerfile                    # Docker 映像檔定義
├── manage.py                     # Django 管理指令
└── README.md                     # 本文件
```

---

## 開發階段

### Phase 0：技術選型與安全邊界定義 ✅

**目標**：明確技術選型與測試範圍

- 選定技術堆疊（Django + PostgreSQL + Session-based Auth + Docker）
- 定義 In Scope / Out of Scope
- 回答：「這個專案刻意不處理哪些攻擊？為什麼？」

**產出**：技術架構文件、Scope Definition

---

### Phase 1：功能設計（攻擊面建模） ⏳

**目標**：在寫程式碼之前，先識別所有潛在攻擊面

**你要完成的重點**：

1. 列出所有功能模組
2. 每個模組標示：
   - 輸入點（user input）
   - 身份/權限邊界
   - 與外部系統的互動
3. 產出一張「文字版 Threat Model」

**判斷你有沒有完成**：

- 能回答：「這個系統有哪些地方不應該信任使用者？」
- 能用 5 分鐘講完整個 attack surface

**常見錯誤（避免）**：

- 功能寫完才想「哪裡可以被打」
- 只想到 SQLi / XSS，沒想到權限與流程問題
- 沒把 admin / internal endpoint 算進來

**產出**：功能規格文件、Attack Surface Map、初版 Threat Model

---

### Phase 2：基礎功能開發（刻意引入漏洞） 🔜

實作 Phase 1 設計的功能，並**刻意**引入特定漏洞供後續學習

---

### Phase 3：威脅建模與修復 🔜

針對 Phase 2 的漏洞進行系統性分析與修復

---

### Phase 4：自動化安全測試（SAST/DAST） 🔜

整合靜態與動態安全測試工具

---

### Phase 5：安全 Code Review 流程 🔜

建立安全程式碼審查的檢查清單與流程

---

## License

本專案僅供教育用途，請勿用於實際生產環境。
