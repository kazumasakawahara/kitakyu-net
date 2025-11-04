# -*- coding: utf-8 -*-
"""
User detail service with comprehensive support information.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from backend.neo4j.client import get_neo4j_client


def _convert_neo4j_types(data: Dict[str, Any]) -> Dict[str, Any]:
    """Neo4jのDateTime/Date型を文字列に変換"""
    result = {}
    for key, value in data.items():
        if value is None:
            result[key] = None
        elif hasattr(value, 'iso_format'):  # Neo4j DateTime/Date
            result[key] = str(value)
        elif isinstance(value, (list, tuple)):
            result[key] = [_convert_neo4j_types(v) if isinstance(v, dict) else str(v) if hasattr(v, 'iso_format') else v for v in value]
        elif isinstance(value, dict):
            result[key] = _convert_neo4j_types(value)
        else:
            result[key] = value
    return result


class UserDetailService:
    """利用者詳細情報サービス"""

    def __init__(self):
        self.db = get_neo4j_client()

    def get_user_detail(self, user_id: str) -> Dict[str, Any]:
        """
        利用者の詳細情報を取得

        Returns:
        - 基本情報
        - 現在利用中のサービス
        - 直近のモニタリング結果
        - 目標達成状況
        - 支援タイムライン
        """
        try:
            # 1. 基本情報
            user_query = """
            MATCH (u:User {user_id: $user_id})
            RETURN u
            """
            user_result = self.db.execute_read(user_query, {"user_id": user_id})

            if not user_result:
                logger.error(f"User {user_id} not found")
                return None

            user_node = _convert_neo4j_types(dict(user_result[0]["u"]))

            # 2. 現在利用中のサービス
            current_services = self._get_current_services(user_id)

            # 3. 直近のモニタリング
            recent_monitoring = self._get_recent_monitoring(user_id)

            # 4. 目標達成状況
            goal_progress = self._get_goal_progress(user_id)

            # 5. 支援タイムライン
            support_timeline = self._get_support_timeline(user_id)

            # 6. アラート情報
            alerts = self._get_alerts(user_id)

            return {
                "user_id": user_id,
                "basic_info": user_node,
                "current_services": current_services,
                "recent_monitoring": recent_monitoring,
                "goal_progress": goal_progress,
                "support_timeline": support_timeline,
                "alerts": alerts
            }

        except Exception as e:
            logger.error(f"Error getting user detail for {user_id}: {e}", exc_info=True)
            raise

    def _get_current_services(self, user_id: str) -> List[Dict[str, Any]]:
        """現在利用中のサービス一覧"""
        query = """
        MATCH (u:User {user_id: $user_id})-[:HAS_PLAN]->(p:Plan)
        WHERE p.status = 'active'
        MATCH (p)-[:INCLUDES_SERVICE]->(s:ServiceNeed)
        RETURN DISTINCT s
        ORDER BY s.service_type
        """
        result = self.db.execute_read(query, {"user_id": user_id})
        return [_convert_neo4j_types(dict(record["s"])) for record in result]

    def _get_recent_monitoring(self, user_id: str) -> Optional[Dict[str, Any]]:
        """直近のモニタリング記録"""
        query = """
        MATCH (u:User {user_id: $user_id})-[:HAS_PLAN]->(p:Plan)
        MATCH (p)-[:HAS_MONITORING]->(m:MonitoringRecord)
        RETURN m
        ORDER BY m.monitoring_date DESC
        LIMIT 1
        """
        result = self.db.execute_read(query, {"user_id": user_id})
        if result:
            monitoring = _convert_neo4j_types(dict(result[0]["m"]))
            # プロパティ名のマッピング（overall_summary → overall_progress, created_by → conducted_by）
            if "overall_summary" in monitoring and "overall_progress" not in monitoring:
                monitoring["overall_progress"] = monitoring["overall_summary"]
            if "created_by" in monitoring and "conducted_by" not in monitoring:
                monitoring["conducted_by"] = monitoring["created_by"]

            # JSON文字列をパース
            if "service_evaluations_json" in monitoring:
                import json
                try:
                    if isinstance(monitoring["service_evaluations_json"], str):
                        monitoring["service_evaluations_json"] = json.loads(monitoring["service_evaluations_json"])
                except:
                    monitoring["service_evaluations_json"] = []

            return monitoring
        return None

    def _get_goal_progress(self, user_id: str) -> List[Dict[str, Any]]:
        """目標達成状況"""
        query = """
        MATCH (u:User {user_id: $user_id})-[:HAS_PLAN]->(p:Plan)
        WHERE p.status = 'active'
        MATCH (p)-[:HAS_GOAL]->(g:Goal)
        RETURN g, p.plan_id as plan_id
        ORDER BY g.priority
        """
        result = self.db.execute_read(query, {"user_id": user_id})

        goals = []
        for record in result:
            goal = _convert_neo4j_types(dict(record["g"]))
            goal["plan_id"] = record["plan_id"]
            goals.append(goal)

        return goals

    def _get_support_timeline(self, user_id: str) -> List[Dict[str, Any]]:
        """支援タイムライン（時系列イベント）"""
        query = """
        MATCH (u:User {user_id: $user_id})-[:HAS_ASSESSMENT]->(a:Assessment)
        OPTIONAL MATCH (u)-[:HAS_PLAN]->(p:Plan)
        OPTIONAL MATCH (p)-[:HAS_MONITORING]->(m:MonitoringRecord)
        RETURN
            'assessment' as event_type,
            a.assessment_id as event_id,
            a.interview_date as event_date,
            'アセスメント実施' as description,
            null as plan_id
        UNION
        MATCH (u:User {user_id: $user_id})-[:HAS_PLAN]->(p:Plan)
        RETURN
            'plan' as event_type,
            p.plan_id as event_id,
            p.created_at as event_date,
            COALESCE(p.plan_type, '個別支援計画') as description,
            p.plan_id as plan_id
        UNION
        MATCH (u:User {user_id: $user_id})-[:HAS_PLAN]->(p:Plan)
        MATCH (p)-[:HAS_MONITORING]->(m:MonitoringRecord)
        RETURN
            'monitoring' as event_type,
            m.monitoring_id as event_id,
            m.monitoring_date as event_date,
            COALESCE(m.overall_progress, 'モニタリング実施') as description,
            p.plan_id as plan_id
        ORDER BY event_date DESC
        LIMIT 20
        """
        result = self.db.execute_read(query, {"user_id": user_id})
        return [_convert_neo4j_types(dict(record)) for record in result]

    def _get_alerts(self, user_id: str) -> List[Dict[str, str]]:
        """アラート情報（契約更新、モニタリング期限等）"""
        alerts = []

        # モニタリング期限チェック
        recent_monitoring = self._get_recent_monitoring(user_id)
        if recent_monitoring:
            monitoring_date_str = recent_monitoring.get("monitoring_date", "")
            if monitoring_date_str:
                try:
                    monitoring_date = datetime.fromisoformat(monitoring_date_str[:10])
                    days_since = (datetime.now() - monitoring_date).days
                    if days_since > 180:  # 6ヶ月以上
                        alerts.append({
                            "type": "monitoring_overdue",
                            "severity": "high",
                            "message": f"モニタリングが{days_since}日実施されていません"
                        })
                    elif days_since > 150:  # 5ヶ月以上
                        alerts.append({
                            "type": "monitoring_reminder",
                            "severity": "medium",
                            "message": "モニタリング実施期限が近づいています"
                        })
                except:
                    pass

        # 計画更新チェック
        plan_query = """
        MATCH (u:User {user_id: $user_id})-[:HAS_PLAN]->(p:Plan)
        WHERE p.status = '実施中'
        RETURN p.plan_end_date as end_date
        ORDER BY p.plan_end_date
        LIMIT 1
        """
        plan_result = self.db.execute_read(plan_query, {"user_id": user_id})
        if plan_result and plan_result[0]["end_date"]:
            end_date_str = str(plan_result[0]["end_date"])[:10]
            try:
                end_date = datetime.fromisoformat(end_date_str)
                days_until = (end_date - datetime.now()).days
                if days_until < 0:
                    alerts.append({
                        "type": "plan_expired",
                        "severity": "high",
                        "message": "支援計画の期限が切れています"
                    })
                elif days_until < 30:
                    alerts.append({
                        "type": "plan_renewal",
                        "severity": "medium",
                        "message": f"支援計画の更新が{days_until}日後に必要です"
                    })
            except:
                pass

        return alerts


def get_user_detail_service() -> UserDetailService:
    """Get user detail service instance."""
    return UserDetailService()
