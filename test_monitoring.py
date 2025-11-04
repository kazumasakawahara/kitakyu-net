#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
モニタリング機能テスト用データ投入スクリプト
"""
import requests
import json
from datetime import datetime, date

API_BASE = "http://localhost:8001/api"

def create_test_assessment(user_id):
    """テスト用アセスメントを作成"""
    assessment_data = {
        "user_id": user_id,
        "interview_date": "2025-03-15",
        "interview_content": """
【日常生活の状況】
・単身生活を送っているが、週1回、家族の支援を受けている
・日中活動への参加が不規則で、週に1-2回程度
・対人関係に不安があり、新しい環境や人との関わりを避ける傾向

【本人の希望】
・もっと安定して日中活動に参加したい
・人とのコミュニケーションが上手くなりたい
・できれば週5日、活動に参加できるようになりたい

【家族の意向】
・本人が安定して通える場所があることを望んでいる
・対人関係のスキルを向上させてほしい
・将来的には就労も視野に入れたい

【健康状態】
・精神障害（統合失調症）で通院中
・服薬管理は自立
・体調の波があり、調子が悪い日は活動参加が難しい

【強み】
・服薬管理ができている
・家族との関係は良好
・活動に参加した際は真面目に取り組む
        """,
        "analyze": False
    }

    response = requests.post(f"{API_BASE}/assessments", json=assessment_data)
    response.raise_for_status()
    assessment = response.json()
    print(f"✅ アセスメント作成成功: {assessment['assessment_id'][:8]}")
    return assessment

def create_test_plan(user_id, assessment_id):
    """テスト用計画を作成"""
    plan_data = {
        "user_id": user_id,
        "assessment_id": assessment_id,
        "plan_type": "個別支援計画",
        "status": "draft",
        "long_term_goals": [
            {
                "goal": "週5日、安定して日中活動に参加できる",
                "period": "2025-04-01〜2026-03-31",
                "criteria": "3ヶ月間、欠席が月2回以内"
            },
            {
                "goal": "対人関係の不安を軽減し、自分から挨拶ができる",
                "period": "2025-04-01〜2026-03-31",
                "criteria": "スタッフや他の利用者に自発的に挨拶ができる"
            }
        ],
        "short_term_goals": [
            {
                "goal": "週3日、日中活動に参加する",
                "period": "2025-04-01〜2025-09-30",
                "criteria": "月12回以上の出席"
            },
            {
                "goal": "スタッフに挨拶ができる",
                "period": "2025-04-01〜2025-09-30",
                "criteria": "朝の挨拶を週3回以上できる"
            }
        ],
        "services": [
            {
                "service_type": "生活介護",
                "facility_name": "A事業所",
                "frequency": "週3日"
            },
            {
                "service_type": "送迎サービス",
                "facility_name": "B事業所",
                "frequency": "利用時毎回"
            }
        ]
    }

    response = requests.post(f"{API_BASE}/plans", json=plan_data)
    response.raise_for_status()
    plan = response.json()
    print(f"✅ 計画作成成功: {plan['plan_id'][:8]}")
    return plan

def create_test_monitoring(plan_id):
    """テスト用モニタリング記録を作成"""

    # 計画詳細を取得して目標IDを取得
    response = requests.get(f"{API_BASE}/plans/{plan_id}")
    response.raise_for_status()
    plan = response.json()

    print(f"📋 取得した計画: plan_id={plan.get('plan_id', 'N/A')[:8]}")

    long_term_goals = plan.get("long_term_goals", [])
    short_term_goals = plan.get("short_term_goals", [])

    print(f"📊 長期目標: {len(long_term_goals)}件, 短期目標: {len(short_term_goals)}件")

    # 目標評価データを作成
    goal_evaluations = []

    # 長期目標の評価
    for i, goal in enumerate(long_term_goals):
        goal_evaluations.append({
            "goal_id": goal["goal_id"],
            "goal_type": "長期",
            "achievement_rate": 60 if i == 0 else 50,
            "achievement_status": "一部達成",
            "evaluation_comment": f"目標{i+1}: 週3回の参加は達成できている。週5回に向けて支援継続中。" if i == 0
                                  else f"目標{i+1}: スタッフへの挨拶は徐々にできるようになってきた。",
            "evidence": "施設記録: 9月の出席率75%（週3.75回）" if i == 0
                       else "スタッフ観察記録: 週2-3回程度、自発的な挨拶が見られる",
            "next_action": "送迎支援を継続し、週4日への参加を目指す" if i == 0
                          else "引き続きSST参加を促し、他利用者への挨拶も練習"
        })

    # 短期目標の評価
    for i, goal in enumerate(short_term_goals):
        goal_evaluations.append({
            "goal_id": goal["goal_id"],
            "goal_type": "短期",
            "achievement_rate": 75 if i == 0 else 60,
            "achievement_status": "達成" if i == 0 else "一部達成",
            "evaluation_comment": f"短期目標{i+1}: 週3回の参加は安定して達成できている。" if i == 0
                                  else f"短期目標{i+1}: スタッフへの挨拶は週2-3回できるようになった。",
            "evidence": "出席記録: 9月は週3.75回出席（目標: 週3回）" if i == 0
                       else "日誌記録参照",
            "next_action": "週4日への参加を目標に段階的に増やす" if i == 0
                          else "他の利用者への挨拶にもチャレンジ"
        })

    # サービスIDを取得（計画から）
    services = plan.get("services", [])
    service_id_1 = services[0].get("service_id", "service_unknown_1") if len(services) > 0 else "service_unknown_1"
    service_id_2 = services[1].get("service_id", "service_unknown_2") if len(services) > 1 else "service_unknown_2"

    monitoring_data = {
        "plan_id": plan_id,
        "monitoring_date": datetime.now().isoformat(),  # Changed from date to datetime
        "monitoring_type": "定期",
        "status": "完了",
        "overall_summary": "週3日の活動参加は安定して達成できている。対人関係への不安は軽減傾向だが、まだ波がある。",
        "strengths": [
            "週3日の活動参加が安定してきた",
            "スタッフとの関係性が良好になってきた",
            "体調管理が改善し、欠席が減少"
        ],
        "challenges": [
            "他の利用者とのコミュニケーションにまだ不安がある",
            "天候や体調による欠席がまだある",
            "新しい活動への参加に消極的"
        ],
        "family_feedback": "家族からは「最近、表情が明るくなってきた」との声あり。活動参加を喜んでいる様子。",
        "goal_evaluations": goal_evaluations,
        "service_evaluations": [
            {
                "service_id": service_id_1,
                "service_name": "生活介護（A事業所）",
                "attendance_rate": 75,
                "service_satisfaction": 4,  # Changed from string to 1-5 rating
                "effectiveness": "活動への参加意欲が高まってきた。スタッフとの関係も良好。",
                "issues": "特になし",
                "adjustment_needed": False
            },
            {
                "service_id": service_id_2,
                "service_name": "送迎サービス（B事業所）",
                "attendance_rate": 100,
                "service_satisfaction": 5,  # Changed from string to 1-5 rating
                "effectiveness": "送迎により確実な出席が可能に。運転手との関係も良好。",
                "issues": "特になし",
                "adjustment_needed": False
            }
        ],
        "plan_revision_needed": False,
        "revision_reason": "",
        "new_goals": [],
        "service_changes": [],
        "created_by": "相談支援専門員_テスト"
    }

    response = requests.post(f"{API_BASE}/monitoring/plans/{plan_id}/monitoring", json=monitoring_data)
    if response.status_code != 201:
        print(f"❌ エラーレスポンス: {response.text}")
    response.raise_for_status()
    monitoring = response.json()
    print(f"✅ モニタリング記録作成成功: {monitoring['monitoring_id'][:8]}")
    return monitoring

def test_monitoring_workflow():
    """モニタリング機能のワークフローをテスト"""
    print("=" * 60)
    print("モニタリング機能テスト開始")
    print("=" * 60)

    # 0. テスト対象の利用者ID
    user_id = "2db3f29f-af9b-4022-b314-f2b80f2c637b"  # テスト太郎
    print(f"\n対象利用者: {user_id[:8]}...")

    # 1. アセスメント作成
    print("\n1️⃣ テスト用アセスメントを作成...")
    assessment = create_test_assessment(user_id)
    assessment_id = assessment["assessment_id"]

    # 2. 計画作成
    print("\n2️⃣ テスト用計画を作成...")
    plan = create_test_plan(user_id, assessment_id)
    plan_id = plan["plan_id"]

    # 3. モニタリング記録作成
    print("\n3️⃣ モニタリング記録を作成...")
    monitoring = create_test_monitoring(plan_id)
    monitoring_id = monitoring["monitoring_id"]

    # 4. モニタリング記録取得
    print("\n4️⃣ モニタリング記録を取得...")
    response = requests.get(f"{API_BASE}/monitoring/{monitoring_id}")
    response.raise_for_status()
    retrieved_monitoring = response.json()
    print(f"✅ モニタリング記録取得成功")
    print(f"   - 記録日: {retrieved_monitoring['monitoring_date']}")
    print(f"   - 種別: {retrieved_monitoring['monitoring_type']}")
    print(f"   - ステータス: {retrieved_monitoring['status']}")
    print(f"   - 目標評価数: {len(retrieved_monitoring['goal_evaluations'])}")

    # 5. 計画のモニタリング記録一覧取得
    print("\n5️⃣ 計画のモニタリング記録一覧を取得...")
    response = requests.get(f"{API_BASE}/monitoring/plans/{plan_id}/monitoring")
    response.raise_for_status()
    monitoring_list = response.json()
    print(f"✅ モニタリング記録一覧取得成功: {len(monitoring_list)}件")

    # 6. 進捗タイムライン取得
    print("\n6️⃣ 進捗タイムラインを取得...")
    response = requests.get(f"{API_BASE}/monitoring/plans/{plan_id}/progress")
    response.raise_for_status()
    timeline = response.json()
    print(f"✅ 進捗タイムライン取得成功: {len(timeline)}個の目標")

    print("\n" + "=" * 60)
    print("✅ すべてのテスト成功！")
    print("=" * 60)
    print(f"\n📝 作成されたデータ:")
    print(f"   - 利用者ID: {user_id}")
    print(f"   - アセスメントID: {assessment_id}")
    print(f"   - 計画ID: {plan_id}")
    print(f"   - モニタリングID: {monitoring_id}")
    print(f"\n🌐 Streamlitで確認:")
    print(f"   http://localhost:8501 → 📊 モニタリング記録ページ")

if __name__ == "__main__":
    try:
        test_monitoring_workflow()
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
