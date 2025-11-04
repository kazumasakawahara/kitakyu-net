# -*- coding: utf-8 -*-
"""
Neo4jスキーマ確認スクリプト
"""
from backend.neo4j.client import get_neo4j_client
from loguru import logger

def check_schema():
    """Neo4jのスキーマを確認"""
    client = get_neo4j_client()

    # ノードラベルを確認
    logger.info("=== ノードラベル一覧 ===")
    label_query = "CALL db.labels() YIELD label RETURN label ORDER BY label"
    labels = client.execute_read(label_query, {})
    for record in labels:
        logger.info(f"- {record['label']}")

    # リレーションシップタイプを確認
    logger.info("\n=== リレーションシップタイプ一覧 ===")
    rel_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType"
    rels = client.execute_read(rel_query, {})
    for record in rels:
        logger.info(f"- {record['relationshipType']}")

    # サンプルPlanの構造を確認
    logger.info("\n=== サンプルPlanの構造 ===")
    plan_query = """
    MATCH (p:Plan)
    OPTIONAL MATCH (p)-[r]->(n)
    RETURN p.plan_id as plan_id, labels(p) as plan_labels,
           type(r) as rel_type, labels(n) as target_labels
    LIMIT 5
    """
    plans = client.execute_read(plan_query, {})
    for record in plans:
        logger.info(f"Plan {record.get('plan_id', 'N/A')}: {record.get('plan_labels')} -[{record.get('rel_type')}]-> {record.get('target_labels')}")


if __name__ == "__main__":
    check_schema()
