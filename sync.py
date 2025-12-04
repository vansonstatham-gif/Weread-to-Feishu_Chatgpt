import os
import requests
import json
from datetime import datetime

# env
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
FEISHU_BASE_ID = os.getenv("FEISHU_BASE_ID")
FEISHU_TABLE_ID = os.getenv("FEISHU_TABLE_ID")
WEREAD_COOKIE = os.getenv("WEREAD_COOKIE")


# -----------------------------
# 1. 获取飞书 tenant_access_token
# -----------------------------
def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    resp = requests.post(url, json={
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    })
    token = resp.json()["tenant_access_token"]
    return token


# -----------------------------
# 2. 获取微信读书数据
# -----------------------------
def common_headers():
    return {
        "Cookie": WEREAD_COOKIE,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Referer": "https://weread.qq.com/",
        "Accept": "application/json, text/plain, */*"
    }


def get_weread_recent_read():
    url = "https://i.weread.qq.com/recent_read"
    resp = requests.get(url, headers=common_headers())

    print("WeRead Status:", resp.status_code)
    print("WeRead Raw Response:", resp.text[:200])

    return resp.json()


def get_weread_bookmark(book_id):
    url = f"https://i.weread.qq.com/book/bookmarklist?bookId={book_id}"
    resp = requests.get(url, headers=common_headers())
    return resp.json()


# -----------------------------
# 3. 写入飞书多维表格
# -----------------------------
def write_to_feishu(token, rows):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BASE_ID}/tables/{FEISHU_TABLE_ID}/records/batch_create"

    data = {
        "records": rows
    }

    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        data=json.dumps(data)
    )

    print("Feishu Response:", resp.text)
    return resp.json()


# -----------------------------
# 4. 主流程
# -----------------------------
def main():
    print("=== Start Sync ===")

    token = get_feishu_token()

    readlog = get_weread_recent_read()

    rows = []
    for item in readlog.get("books", []):
        book = item.get("book", {})
        rows.append({
            "fields": {
                "书名": book.get("title"),
                "作者": book.get("author"),
                "阅读进度": f"{item.get('readProgress', 0)}%",
                "更新时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        })

    if rows:
        write_to_feishu(token, rows)

    print("=== Done ===")


if __name__ == "__main__":
    main()
