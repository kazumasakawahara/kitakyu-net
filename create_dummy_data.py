# -*- coding: utf-8 -*-
"""
ダミーデータ作成スクリプト
全利用者にアセスメントと計画を作成
"""
import requests
from datetime import date, timedelta
from loguru import logger

API_BASE_URL = "http://localhost:8001/api"

def create_assessment_and_plan(user_id: str, user_name: str):
    """利用者にアセスメントと計画を作成"""

    # 1. アセスメント作成
    interview_content = f"""
【面談日】{(date.today() - timedelta(days=90)).isoformat()}

【本人の状況】
{user_name}さんは現在、家族と同居しています。日常生活は概ね自立していますが、一部支援が必要な場面もあります。
健康状態は良好で、定期的な通院を継続されています。

【本人の希望】
・就労に向けたスキルアップがしたい
・人との交流の機会を増やしたい
・自立した生活を目指したい

【家族の意向】
・安心して通える場所を見つけたい
・将来の自立に向けた支援を受けさせたい

【専門的視点からの分析】
・コミュニケーション能力の向上が必要
・生活リズムの安定化が課題
・社会参加の促進が重要

【強み】
・真面目で継続力がある
・新しいことに挑戦する意欲がある
・家族のサポートが得られる

【課題】
・対人場面での緊張が強い
・体調管理に課題がある

【支援の方向性】
就労継続支援B型を活用し、作業スキルとコミュニケーション能力の向上を図る。
家族は本人の自立を応援しており、協力的です。
"""

    assessment_data = {
        "user_id": user_id,
        "interview_date": (date.today() - timedelta(days=90)).isoformat(),
        "interview_content": interview_content.strip(),
        "analyze": False  # LLM分析はスキップ
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/assessments",
            json=assessment_data,
            timeout=10
        )
        response.raise_for_status()
        assessment = response.json()
        assessment_id = assessment["assessment_id"]
        logger.info(f"✅ アセスメント作成: {user_name} - {assessment_id[:8]}")
    except Exception as e:
        logger.error(f"❌ アセスメント作成失敗: {user_name} - {e}")
        return False

    # 2. 計画作成
    plan_start = date.today() - timedelta(days=60)

    plan_data = {
        "user_id": user_id,
        "assessment_id": assessment_id,
        "plan_type": "個別支援計画",
        "status": "active",
        "long_term_goals": [
            {
                "goal": "就労に必要なスキルを身につけ、安定した作業ができるようになる",
                "period": "1年",
                "criteria": "週5日、安定して作業に取り組むことができる"
            },
            {
                "goal": "地域や事業所で良好な人間関係を築き、社会参加を広げる",
                "period": "1年",
                "criteria": "事業所内で複数の利用者と会話ができる"
            }
        ],
        "short_term_goals": [
            {
                "goal": "週5日、就労継続支援B型事業所に通所する",
                "period": "6ヶ月",
                "criteria": "出席率80%以上を維持する"
            },
            {
                "goal": "作業場面で他の利用者とコミュニケーションを取る",
                "period": "6ヶ月",
                "criteria": "グループワークで自ら発言できる"
            }
        ],
        "services": [
            {
                "service_type": "就労継続支援B型",
                "facility_name": "ワークセンター希望",
                "frequency": "週5日",
                "start_date": plan_start.isoformat()
            }
        ]
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/plans",
            json=plan_data,
            timeout=10
        )
        response.raise_for_status()
        plan = response.json()
        plan_id = plan["plan_id"]
        logger.info(f"✅ 計画作成: {user_name} - {plan_id[:8]}")
        return True
    except Exception as e:
        logger.error(f"❌ 計画作成失敗: {user_name} - {e}")
        return False


def main():
    """全利用者にダミーデータを作成"""

    print("=" * 60)
    print("ダミーデータ作成開始")
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

            print(f"処理中: {user_name} ({user_id[:8]}...)")

            if create_assessment_and_plan(user_id, user_name):
                success_count += 1

            print()

        print("=" * 60)
        print(f"完了: {success_count}/{len(users)}件")
        print("=" * 60)

    except Exception as e:
        logger.error(f"エラー: {e}")


if __name__ == "__main__":
    main()
