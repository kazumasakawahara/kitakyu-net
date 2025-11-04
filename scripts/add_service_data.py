# -*- coding: utf-8 -*-
"""
モニタリングデータに基づいてServiceNeedノードを作成
"""
import sys
import os
from loguru import logger

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.neo4j.client import get_neo4j_client


def create_service_nodes():
    """ServiceNeedノードとINCLUDES_SERVICE関係性を作成"""

    client = get_neo4j_client()

    # テスト太郎のactiveなPlan IDを取得
    plan_query = """
    MATCH (u:User {name: 'テスト太郎'})-[:HAS_PLAN]->(p:Plan)
    WHERE p.status = 'active'
    RETURN p.plan_id as plan_id
    """

    plan_result = client.execute_read(plan_query)
    if not plan_result:
        logger.error("テスト太郎のactiveなPlanが見つかりません")
        return False

    plan_id = plan_result[0]["plan_id"]
    logger.info(f"Plan ID: {plan_id}")

    # ServiceNeedノード作成とINCLUDES_SERVICE関係性作成のクエリ
    service_data = [
        {
            "service_id": "service_a_seikatsu_kaigo",
            "service_type": "生活介護",
            "facility_name": "A事業所",
            "frequency": "週5日",
            "start_date": "2024-04-01",
            "notes": "活動への参加意欲が高まってきた。スタッフとの関係も良好。"
        },
        {
            "service_id": "service_b_sougei",
            "service_type": "送迎サービス",
            "facility_name": "B事業所",
            "frequency": "週5日",
            "start_date": "2024-04-01",
            "notes": "送迎により確実な出席が可能に。運転手との関係も良好。"
        }
    ]

    create_query = """
    MATCH (p:Plan {plan_id: $plan_id})
    MERGE (s:ServiceNeed {service_id: $service_id})
    SET s.service_type = $service_type,
        s.facility_name = $facility_name,
        s.frequency = $frequency,
        s.start_date = date($start_date),
        s.notes = $notes,
        s.updated_at = datetime()
    MERGE (p)-[:INCLUDES_SERVICE]->(s)
    RETURN s.service_id as service_id, s.service_type as service_type, s.facility_name as facility_name
    """

    for service in service_data:
        params = {
            "plan_id": plan_id,
            **service
        }

        result = client.execute_write(create_query, params)

        if result:
            logger.success(f"✅ ServiceNeed作成成功: {result[0]['service_type']} ({result[0]['facility_name']})")
        else:
            logger.error(f"❌ ServiceNeed作成失敗: {service['service_type']}")

    # 検証クエリ
    verify_query = """
    MATCH (p:Plan {plan_id: $plan_id})-[:INCLUDES_SERVICE]->(s:ServiceNeed)
    RETURN s.service_type as service_type, s.facility_name as facility_name
    ORDER BY s.service_type
    """

    verification = client.execute_read(verify_query, {"plan_id": plan_id})

    logger.info(f"\n=== 検証結果 ===")
    logger.info(f"作成されたServiceNeed: {len(verification)}件")
    for svc in verification:
        logger.info(f"  - {svc['service_type']} ({svc['facility_name']})")

    return True


if __name__ == "__main__":
    logger.info("=== ServiceNeedノード作成開始 ===\n")

    success = create_service_nodes()

    if success:
        logger.success("\n✅ ServiceNeedノードとINCLUDES_SERVICE関係性の作成が完了しました")
        logger.info("\nフロントエンドで確認してください:")
        logger.info("  1. Streamlit再起動")
        logger.info("  2. 利用者詳細ページでテスト太郎を選択")
        logger.info("  3. 「現在利用中のサービス」セクションにA事業所とB事業所が表示されることを確認")
    else:
        logger.error("\n❌ ServiceNeed作成に失敗しました")
