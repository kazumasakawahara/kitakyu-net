# -*- coding: utf-8 -*-
"""
手帳情報追加スクリプト
既存利用者に手帳情報を追加
"""
import requests
from datetime import date, timedelta
from loguru import logger

API_BASE_URL = "http://localhost:8000/api"

# 手帳情報マッピング
NOTEBOOK_DATA = {
    "テスト太郎": {
        "disability_type": "精神障害",
        "mental_health_notebook": True,
        "mental_health_notebook_grade": "2級",
        "mental_health_notebook_expiry": (date.today() + timedelta(days=300)).isoformat()
    },
    "佐藤栄作": {
        "disability_type": "知的障害（発達障害）",
        "therapy_notebook": True,
        "therapy_notebook_grade": "B1"
    },
    "山田太郎": {
        "disability_type": "知的障害",
        "therapy_notebook": True,
        "therapy_notebook_grade": "A"
    },
    "河原一雅": {
        "disability_type": "知的障害",
        "therapy_notebook": True,
        "therapy_notebook_grade": "B2"
    },
    "鈴木一郎": {
        "disability_type": "知的障害, 精神障害",
        "therapy_notebook": True,
        "therapy_notebook_grade": "A3",
        "mental_health_notebook": True,
        "mental_health_notebook_grade": "3級",
        "mental_health_notebook_expiry": (date.today() + timedelta(days=60)).isoformat()
    }
}

def update_user_notebook(user_id: str, user_name: str, notebook_info: dict):
    """利用者の手帳情報を更新"""
    try:
        response = requests.put(
            f"{API_BASE_URL}/users/{user_id}",
            json=notebook_info,
            timeout=10
        )
        response.raise_for_status()
        logger.success(f"✅ 手帳情報更新: {user_name}")

        # 更新内容を表示
        if notebook_info.get("therapy_notebook"):
            logger.info(f"  療育手帳: {notebook_info.get('therapy_notebook_grade', '')}")
        if notebook_info.get("mental_health_notebook"):
            expiry = notebook_info.get("mental_health_notebook_expiry", '')
            logger.info(f"  精神保健福祉手帳: {notebook_info.get('mental_health_notebook_grade', '')} (有効期限: {expiry})")

        return True
    except Exception as e:
        logger.error(f"❌ 手帳情報更新失敗: {user_name} - {e}")
        return False


def main():
    """全利用者の手帳情報を更新"""
    print("=" * 60)
    print("手帳情報追加開始")
    print("=" * 60)

    # 利用者一覧取得
    try:
        response = requests.get(
            f"{API_BASE_URL}/users",
            params={"page": 1, "page_size": 100},
            timeout=10
        )
        response.raise_for_status()
        users_data = response.json()
        users = users_data.get("users", [])

        print(f"\n対象利用者: {len(users)}件\n")

        success_count = 0
        for user in users:
            user_id = user["user_id"]
            user_name = user["name"]

            # 手帳情報がある場合のみ更新
            if user_name in NOTEBOOK_DATA:
                notebook_info = NOTEBOOK_DATA[user_name]
                print(f"処理中: {user_name} ({user_id[:8]}...)")

                if update_user_notebook(user_id, user_name, notebook_info):
                    success_count += 1
                print()
            else:
                print(f"スキップ: {user_name} (手帳情報なし)")

        print("=" * 60)
        print(f"完了: {success_count}/{len(NOTEBOOK_DATA)}件")
        print("=" * 60)

    except Exception as e:
        logger.error(f"エラー: {e}")


if __name__ == "__main__":
    main()
