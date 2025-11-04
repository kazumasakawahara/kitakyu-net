# -*- coding: utf-8 -*-
"""
利用者詳細機能のテストスクリプト
"""
import requests
from loguru import logger

API_BASE_URL = "http://localhost:8001/api"


def get_test_user():
    """テスト用の利用者を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/users", params={"page": 1, "page_size": 10})
        response.raise_for_status()
        users_data = response.json()
        users = users_data.get("users", [])

        if not users:
            logger.error("利用者が見つかりません")
            return None

        user = users[0]
        logger.info(f"利用者: {user['name']} (ID: {user['user_id']})")
        return user

    except Exception as e:
        logger.error(f"利用者取得エラー: {e}")
        return None


def test_user_detail(user_id: str):
    """利用者詳細情報のテスト"""
    try:
        logger.info("\n=== 利用者詳細情報テスト ===")
        response = requests.get(f"{API_BASE_URL}/users/{user_id}/detail", timeout=30)
        response.raise_for_status()

        detail = response.json()
        logger.success("✅ 詳細情報取得成功")

        # 基本情報
        basic_info = detail.get("basic_info", {})
        logger.info(f"\n【基本情報】")
        logger.info(f"  氏名: {basic_info.get('name', '')}")
        logger.info(f"  カナ: {basic_info.get('name_kana', '')}")
        logger.info(f"  性別: {basic_info.get('gender', '')}")
        logger.info(f"  生年月日: {basic_info.get('birth_date', '')[:10] if basic_info.get('birth_date') else ''}")
        logger.info(f"  障害種別: {basic_info.get('disability_type', '')}")
        logger.info(f"  支援区分: {basic_info.get('support_level', '')}")
        logger.info(f"  居住状況: {basic_info.get('living_situation', '')}")

        # 現在利用中のサービス
        current_services = detail.get("current_services", [])
        logger.info(f"\n【現在利用中のサービス】: {len(current_services)}件")
        for service in current_services:
            logger.info(f"  - {service.get('service_type', '')} ({service.get('facility_name', '')})")

        # 直近のモニタリング
        recent_monitoring = detail.get("recent_monitoring")
        if recent_monitoring:
            logger.info(f"\n【直近のモニタリング】")
            logger.info(f"  実施日: {recent_monitoring.get('monitoring_date', '')[:10] if recent_monitoring.get('monitoring_date') else ''}")
            logger.info(f"  全体進捗: {recent_monitoring.get('overall_progress', '')}")
            logger.info(f"  実施者: {recent_monitoring.get('conducted_by', '')}")
        else:
            logger.info(f"\n【直近のモニタリング】: なし")

        # 目標達成状況
        goal_progress = detail.get("goal_progress", [])
        logger.info(f"\n【目標達成状況】: {len(goal_progress)}件")
        for goal in goal_progress:
            logger.info(f"  - {goal.get('goal_type', '')}: {goal.get('goal_text', goal.get('goal', ''))[:30]}...")
            logger.info(f"    状況: {goal.get('achievement_status', '未設定')}")

        # 支援タイムライン
        support_timeline = detail.get("support_timeline", [])
        logger.info(f"\n【支援タイムライン】: {len(support_timeline)}件（最新5件表示）")
        for event in support_timeline[:5]:
            event_type = event.get("event_type", "")
            event_date = event.get("event_date", "")[:10] if event.get("event_date") else ""
            description = event.get("description", "")

            type_label_map = {
                "assessment": "アセスメント",
                "plan": "支援計画",
                "monitoring": "モニタリング"
            }
            type_label = type_label_map.get(event_type, event_type)

            logger.info(f"  {event_date} - {type_label}: {description}")

        # アラート情報
        alerts = detail.get("alerts", [])
        logger.info(f"\n【アラート】: {len(alerts)}件")
        for alert in alerts:
            severity = alert.get("severity", "")
            message = alert.get("message", "")
            severity_icon = {"high": "🚨", "medium": "⚠️", "low": "ℹ️"}.get(severity, "📌")
            logger.info(f"  {severity_icon} [{severity}] {message}")

        if not alerts:
            logger.info("  ✅ 期限内です")

        return True

    except Exception as e:
        logger.error(f"❌ 詳細情報取得失敗: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        return False


if __name__ == "__main__":
    logger.info("=== 利用者詳細機能テスト開始 ===\n")

    # 1. テストデータ取得
    user = get_test_user()
    if not user:
        logger.error("利用者が見つかりません。テスト終了。")
        exit(1)

    user_id = user["user_id"]

    # 2. 詳細情報テスト
    result = test_user_detail(user_id)

    # 3. 結果サマリー
    logger.info("\n=== テスト結果 ===")
    if result:
        logger.success("✅ 利用者詳細機能テスト完了")
    else:
        logger.error("❌ テスト失敗")
