# -*- coding: utf-8 -*-
"""
モニタリング機能のテストスクリプト
"""
import requests
from datetime import datetime, date
from loguru import logger

API_BASE_URL = "http://localhost:8001/api"


def get_first_plan():
    """最初の計画を取得"""
    try:
        # 最初の利用者を取得
        response = requests.get(f"{API_BASE_URL}/users", params={"page": 1, "page_size": 10})
        response.raise_for_status()
        users_data = response.json()
        users = users_data.get("users", [])

        if not users:
            logger.error("利用者が見つかりません")
            return None, None

        user_id = users[0]["user_id"]
        logger.info(f"利用者ID: {user_id} ({users[0]['name']})")

        # 利用者の計画を取得
        response = requests.get(f"{API_BASE_URL}/plans/user/{user_id}")
        response.raise_for_status()
        plans = response.json()

        if not plans:
            logger.error(f"利用者 {user_id} の計画が見つかりません")
            return None, None

        plan = plans[0]
        logger.info(f"計画ID: {plan['plan_id']}")
        return user_id, plan

    except Exception as e:
        logger.error(f"エラー: {e}")
        return None, None


def create_test_monitoring(plan_id: str, plan: dict):
    """テストモニタリング記録を作成"""

    # 目標評価を作成
    goal_evaluations = []

    # 長期目標の評価
    for goal in plan.get("long_term_goals", [])[:2]:  # 最初の2つだけ
        goal_evaluations.append({
            "goal_id": goal["goal_id"],
            "goal_type": "long_term",
            "achievement_rate": 70,
            "evaluation_comment": "順調に進捗しています。本人の努力が見られます。",
            "achievement_status": "一部達成",
            "evidence": "デイケアでの作業が丁寧にできるようになった",
            "next_action": "引き続き同様の支援を継続"
        })

    # 短期目標の評価
    for goal in plan.get("short_term_goals", [])[:2]:  # 最初の2つだけ
        goal_evaluations.append({
            "goal_id": goal["goal_id"],
            "goal_type": "short_term",
            "achievement_rate": 80,
            "evaluation_comment": "目標に向けて順調に進んでいます。",
            "achievement_status": "一部達成",
            "evidence": "週2回のデイケア参加を継続できている",
            "next_action": "引き続き参加を促す"
        })

    # サービス評価を作成
    service_evaluations = []
    for service in plan.get("services", [])[:2]:  # 最初の2つだけ
        service_evaluations.append({
            "service_id": service.get("service_id", "service_001"),
            "service_type": service.get("service_type", "デイケア"),
            "facility_name": service.get("facility_name", "〇〇精神科クリニック"),
            "usage_status": "適切",
            "satisfaction_level": "満足",
            "evaluation_comment": "本人に合ったプログラムで、安定して利用できている",
            "effectiveness": "効果的",
            "continuation_recommendation": "継続"
        })

    # モニタリング記録データ
    monitoring_data = {
        "plan_id": plan_id,
        "monitoring_date": date.today().isoformat(),
        "monitoring_type": "定期",
        "status": "完了",
        "overall_summary": """
【全体評価】
本人は支援計画に沿って順調に生活を送っています。デイケアへの参加が安定しており、
対人関係のスキルも少しずつ向上しています。

【進捗状況】
- 長期目標: 就労継続支援B型への移行準備として、作業スキルが向上しています (達成率70%)
- 短期目標: デイケアでの対人交流が増えてきました (達成率80%)

【今後の方針】
現在のサービスを継続しながら、就労継続支援B型事業所の見学を計画します。
        """.strip(),
        "strengths": [
            "デイケアへの参加が安定している",
            "作業が丁寧で、集中して取り組める",
            "服薬管理が自分でできている",
            "スタッフとの関係が良好"
        ],
        "challenges": [
            "初対面の人との会話にまだ不安がある",
            "複雑な指示の理解に時間がかかる",
            "午後は疲れやすく、休憩が必要"
        ],
        "goal_evaluations": goal_evaluations,
        "service_evaluations": service_evaluations,
        "family_feedback": "本人が楽しくデイケアに通えているので、安心しています。今後も無理のない範囲で支援をお願いします。",
        "plan_revision_needed": False,
        "revision_reason": "",
        "new_goals": [],
        "service_changes": [],
        "created_by": "staff_test"
    }

    try:
        logger.info(f"モニタリング記録作成開始 (Plan: {plan_id})")
        response = requests.post(
            f"{API_BASE_URL}/monitoring/plans/{plan_id}/monitoring",
            json=monitoring_data,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        logger.success(f"✅ モニタリング記録作成成功")
        logger.info(f"Monitoring ID: {result['monitoring_id']}")
        logger.info(f"記録日: {result['monitoring_date'][:10]}")
        logger.info(f"種別: {result['monitoring_type']}")
        logger.info(f"ステータス: {result['status']}")
        logger.info(f"目標評価数: {len(result.get('goal_evaluations', []))}")
        logger.info(f"サービス評価数: {len(result.get('service_evaluations', []))}")

        return result

    except Exception as e:
        logger.error(f"❌ モニタリング記録作成失敗: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        return None


def list_monitoring_records(plan_id: str):
    """モニタリング記録一覧を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/monitoring/plans/{plan_id}/monitoring")
        response.raise_for_status()

        records = response.json()
        logger.info(f"モニタリング記録数: {len(records)}")

        for i, record in enumerate(records, 1):
            logger.info(f"\n--- 記録 {i} ---")
            logger.info(f"ID: {record['monitoring_id']}")
            logger.info(f"記録日: {record['monitoring_date'][:10]}")
            logger.info(f"種別: {record['monitoring_type']}")
            logger.info(f"ステータス: {record['status']}")

        return records

    except Exception as e:
        logger.error(f"モニタリング記録一覧取得失敗: {e}")
        return []


def get_progress_timeline(plan_id: str):
    """進捗タイムラインを取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/monitoring/plans/{plan_id}/progress")
        response.raise_for_status()

        timeline = response.json()
        logger.info(f"\n=== 進捗タイムライン ===")
        logger.info(f"目標数: {len(timeline)}")

        for goal_timeline in timeline:
            logger.info(f"\n目標: {goal_timeline['goal_text'][:50]}...")
            logger.info(f"種別: {goal_timeline['goal_type']}")
            logger.info(f"評価回数: {len(goal_timeline['timeline'])}")

            for point in goal_timeline['timeline']:
                logger.info(f"  - {point['date'][:10]}: {point['achievement_rate']}% ({point['status']})")

        return timeline

    except Exception as e:
        logger.error(f"進捗タイムライン取得失敗: {e}")
        return []


if __name__ == "__main__":
    logger.info("=== モニタリング機能テスト開始 ===\n")

    # 1. 計画を取得
    user_id, plan = get_first_plan()
    if not plan:
        logger.error("計画が見つかりません。テスト終了。")
        exit(1)

    plan_id = plan["plan_id"]

    # 2. モニタリング記録を作成
    logger.info("\n=== モニタリング記録作成 ===")
    monitoring = create_test_monitoring(plan_id, plan)

    if monitoring:
        # 3. モニタリング記録一覧を取得
        logger.info("\n=== モニタリング記録一覧取得 ===")
        records = list_monitoring_records(plan_id)

        # 4. 進捗タイムラインを取得
        logger.info("\n=== 進捗タイムライン取得 ===")
        timeline = get_progress_timeline(plan_id)

        logger.success("\n✅ すべてのテスト完了")
    else:
        logger.error("\n❌ テスト失敗")
