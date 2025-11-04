# -*- coding: utf-8 -*-
"""
Monitoring service for care plan monitoring records.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class MonitoringService:
    """モニタリング記録管理サービス"""

    def __init__(self):
        """Initialize monitoring service."""
        from backend.neo4j.client import get_neo4j_client
        self.db = get_neo4j_client()

    def close(self):
        """Close database connection."""
        # Connection is managed by Neo4jClient
        pass

    def create_monitoring_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new monitoring record.

        Args:
            record_data: Monitoring record data

        Returns:
            Created monitoring record
        """
        monitoring_id = f"mon_{uuid.uuid4().hex[:12]}"
        now = datetime.now()

        try:
            logger.debug(f"Creating monitoring record for plan: {record_data.get('plan_id')}")
            logger.debug(f"Goal evaluations count: {len(record_data.get('goal_evaluations', []))}")

            # Create main monitoring record
            monitoring_node = self._create_monitoring_node(monitoring_id, record_data, now)

            # Create goal evaluations
            if "goal_evaluations" in record_data:
                self._create_goal_evaluations(monitoring_id, record_data["goal_evaluations"])

            # Store service evaluations and other JSON data
            self._store_additional_data(monitoring_id, record_data)

            logger.info(f"Created monitoring record: {monitoring_id}")
            # Return with original data structures (not JSON strings)
            return {
                **monitoring_node,
                "goal_evaluations": record_data.get("goal_evaluations", []),
                "service_evaluations": record_data.get("service_evaluations", []),
                "new_goals": record_data.get("new_goals", []),
                "service_changes": record_data.get("service_changes", [])
            }
        except Exception as e:
            logger.error(f"Error creating monitoring record: {e}", exc_info=True)
            raise

    def _create_monitoring_node(self, monitoring_id: str, record_data: Dict[str, Any], now: datetime) -> Dict[str, Any]:
        """Create monitoring record node."""
        # Handle monitoring_date - can be datetime object or ISO string
        monitoring_date = record_data["monitoring_date"]
        if isinstance(monitoring_date, datetime):
            monitoring_date_str = monitoring_date.isoformat()
        else:
            monitoring_date_str = monitoring_date  # Already a string

        query = """
        MATCH (p:Plan {plan_id: $plan_id})
        CREATE (m:MonitoringRecord {
            monitoring_id: $monitoring_id,
            plan_id: $plan_id,
            monitoring_date: datetime($monitoring_date),
            monitoring_type: $monitoring_type,
            status: $status,
            overall_summary: $overall_summary,
            strengths: $strengths,
            challenges: $challenges,
            family_feedback: $family_feedback,
            plan_revision_needed: $plan_revision_needed,
            revision_reason: $revision_reason,
            created_by: $created_by,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at)
        })
        CREATE (p)-[:HAS_MONITORING]->(m)
        RETURN m
        """

        params = {
            "monitoring_id": monitoring_id,
            "plan_id": record_data["plan_id"],
            "monitoring_date": monitoring_date_str,
            "monitoring_type": record_data["monitoring_type"],
            "status": record_data["status"],
            "overall_summary": record_data["overall_summary"],
            "strengths": record_data.get("strengths", []),
            "challenges": record_data.get("challenges", []),
            "family_feedback": record_data.get("family_feedback"),
            "plan_revision_needed": record_data.get("plan_revision_needed", False),
            "revision_reason": record_data.get("revision_reason"),
            "created_by": record_data["created_by"],
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }

        try:
            result = self.db.execute_write(query, params)
        except Exception as e:
            logger.error(f"Neo4j query failed in _create_monitoring_node: {e}", exc_info=True)
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise

        if not result:
            logger.error(f"Failed to create monitoring record for plan: {record_data['plan_id']}")
            raise Exception("Failed to create monitoring record")

        # Convert Neo4j datetime objects to Python datetime
        node_data = dict(result[0]["m"])
        if "monitoring_date" in node_data and hasattr(node_data["monitoring_date"], "to_native"):
            node_data["monitoring_date"] = node_data["monitoring_date"].to_native()
        if "created_at" in node_data and hasattr(node_data["created_at"], "to_native"):
            node_data["created_at"] = node_data["created_at"].to_native()
        if "updated_at" in node_data and hasattr(node_data["updated_at"], "to_native"):
            node_data["updated_at"] = node_data["updated_at"].to_native()

        return node_data

    def _create_goal_evaluations(self, monitoring_id: str, goal_evaluations: List[Dict[str, Any]]) -> None:
        """Create goal evaluation relationships."""
        for goal_eval in goal_evaluations:
            query = """
            MATCH (m:MonitoringRecord {monitoring_id: $monitoring_id})
            MATCH (g:Goal {goal_id: $goal_id})
            CREATE (m)-[:EVALUATES {
                achievement_rate: $achievement_rate,
                evaluation_comment: $evaluation_comment,
                achievement_status: $achievement_status,
                evidence: $evidence,
                next_action: $next_action
            }]->(g)
            """

            params = {
                "monitoring_id": monitoring_id,
                "goal_id": goal_eval["goal_id"],
                "achievement_rate": goal_eval["achievement_rate"],
                "evaluation_comment": goal_eval["evaluation_comment"],
                "achievement_status": goal_eval["achievement_status"],
                "evidence": goal_eval.get("evidence"),
                "next_action": goal_eval.get("next_action")
            }

            self.db.execute_write(query, params)

    def _store_additional_data(self, monitoring_id: str, record_data: Dict[str, Any]) -> None:
        """Store service evaluations, new goals, and service changes as JSON properties."""
        import json

        if "service_evaluations" in record_data and record_data["service_evaluations"]:
            query = """
            MATCH (m:MonitoringRecord {monitoring_id: $monitoring_id})
            SET m.service_evaluations_json = $service_evaluations_json
            """
            params = {
                "monitoring_id": monitoring_id,
                "service_evaluations_json": json.dumps(record_data["service_evaluations"], ensure_ascii=False)
            }
            self.db.execute_write(query, params)

        if "new_goals" in record_data and record_data["new_goals"]:
            query = """
            MATCH (m:MonitoringRecord {monitoring_id: $monitoring_id})
            SET m.new_goals_json = $new_goals_json
            """
            params = {
                "monitoring_id": monitoring_id,
                "new_goals_json": json.dumps(record_data["new_goals"], ensure_ascii=False)
            }
            self.db.execute_write(query, params)

        if "service_changes" in record_data and record_data["service_changes"]:
            query = """
            MATCH (m:MonitoringRecord {monitoring_id: $monitoring_id})
            SET m.service_changes_json = $service_changes_json
            """
            params = {
                "monitoring_id": monitoring_id,
                "service_changes_json": json.dumps(record_data["service_changes"], ensure_ascii=False)
            }
            self.db.execute_write(query, params)

    def get_monitoring_record(self, monitoring_id: str) -> Optional[Dict[str, Any]]:
        """
        Get monitoring record by ID.

        Args:
            monitoring_id: Monitoring record ID

        Returns:
            Monitoring record or None
        """
        import json

        # Get monitoring record node
        query = """
        MATCH (m:MonitoringRecord {monitoring_id: $monitoring_id})
        RETURN m
        """

        result = self.db.execute_read(query, {"monitoring_id": monitoring_id})
        if not result:
            return None

        monitoring_node = dict(result[0]["m"])

        # Convert Neo4j datetime objects to Python datetime
        if "monitoring_date" in monitoring_node and hasattr(monitoring_node["monitoring_date"], "to_native"):
            monitoring_node["monitoring_date"] = monitoring_node["monitoring_date"].to_native()
        if "created_at" in monitoring_node and hasattr(monitoring_node["created_at"], "to_native"):
            monitoring_node["created_at"] = monitoring_node["created_at"].to_native()
        if "updated_at" in monitoring_node and hasattr(monitoring_node["updated_at"], "to_native"):
            monitoring_node["updated_at"] = monitoring_node["updated_at"].to_native()

        # Get goal evaluations
        goal_eval_query = """
        MATCH (m:MonitoringRecord {monitoring_id: $monitoring_id})-[r:EVALUATES]->(g:Goal)
        RETURN g.goal_id as goal_id, g.goal_type as goal_type,
               r.achievement_rate as achievement_rate,
               r.evaluation_comment as evaluation_comment,
               r.achievement_status as achievement_status,
               r.evidence as evidence,
               r.next_action as next_action
        """

        goal_results = self.db.execute_read(goal_eval_query, {"monitoring_id": monitoring_id})
        goal_evaluations = [dict(record) for record in goal_results]

        # Parse JSON strings back to dicts
        service_evaluations = []
        if "service_evaluations_json" in monitoring_node and monitoring_node["service_evaluations_json"]:
            service_evaluations = json.loads(monitoring_node["service_evaluations_json"])

        new_goals = []
        if "new_goals_json" in monitoring_node and monitoring_node["new_goals_json"]:
            new_goals = json.loads(monitoring_node["new_goals_json"])

        service_changes = []
        if "service_changes_json" in monitoring_node and monitoring_node["service_changes_json"]:
            service_changes = json.loads(monitoring_node["service_changes_json"])

        return {
            **monitoring_node,
            "goal_evaluations": goal_evaluations,
            "service_evaluations": service_evaluations,
            "new_goals": new_goals,
            "service_changes": service_changes
        }

    def list_monitoring_records_by_plan(self, plan_id: str) -> List[Dict[str, Any]]:
        """
        List all monitoring records for a plan.

        Args:
            plan_id: Plan ID

        Returns:
            List of monitoring records
        """
        # Get all monitoring record IDs for this plan
        query = """
        MATCH (p:Plan {plan_id: $plan_id})-[:HAS_MONITORING]->(m:MonitoringRecord)
        RETURN m.monitoring_id as monitoring_id
        ORDER BY m.monitoring_date DESC
        """

        results = self.db.execute_read(query, {"plan_id": plan_id})

        # Get full details for each monitoring record
        records = []
        for result in results:
            monitoring_id = result["monitoring_id"]
            record = self.get_monitoring_record(monitoring_id)
            if record:
                records.append(record)

        return records

    @staticmethod
    def _list_monitoring_records_by_plan_tx(tx, plan_id: str):
        """Transaction: List monitoring records by plan."""

        query = """
        MATCH (p:Plan {plan_id: $plan_id})-[:HAS_MONITORING]->(m:MonitoringRecord)
        RETURN m
        ORDER BY m.monitoring_date DESC
        """

        result = tx.run(query, plan_id=plan_id)
        records = []

        for record in result:
            monitoring_node = dict(record["m"])
            monitoring_id = monitoring_node["monitoring_id"]

            # Get goal evaluations for each record
            goal_eval_query = """
            MATCH (m:MonitoringRecord {monitoring_id: $monitoring_id})-[r:EVALUATES]->(g:Goal)
            RETURN g.goal_id as goal_id, g.goal_type as goal_type,
                   r.achievement_rate as achievement_rate,
                   r.evaluation_comment as evaluation_comment,
                   r.achievement_status as achievement_status,
                   r.evidence as evidence,
                   r.next_action as next_action
            """

            goal_results = tx.run(goal_eval_query, monitoring_id=monitoring_id)
            goal_evaluations = [dict(rec) for rec in goal_results]

            records.append({
                **monitoring_node,
                "goal_evaluations": goal_evaluations,
                "service_evaluations": monitoring_node.get("service_evaluations", []),
                "new_goals": monitoring_node.get("new_goals", []),
                "service_changes": monitoring_node.get("service_changes", [])
            })

        return records

    def update_monitoring_record(self, monitoring_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update monitoring record.

        Args:
            monitoring_id: Monitoring record ID
            update_data: Update data

        Returns:
            Updated monitoring record
        """
        with self.driver.session(database=self.database) as session:
            result = session.execute_write(
                self._update_monitoring_record_tx,
                monitoring_id,
                update_data
            )

        logger.info(f"Updated monitoring record: {monitoring_id}")
        return result

    @staticmethod
    def _update_monitoring_record_tx(tx, monitoring_id: str, update_data: Dict[str, Any]):
        """Transaction: Update monitoring record."""

        # Build SET clause dynamically
        set_clauses = []
        params = {"monitoring_id": monitoring_id}

        simple_fields = [
            "monitoring_date", "monitoring_type", "status", "overall_summary",
            "family_feedback", "plan_revision_needed", "revision_reason"
        ]

        for field in simple_fields:
            if field in update_data:
                if field == "monitoring_date" and update_data[field]:
                    set_clauses.append(f"m.{field} = datetime($update_{field})")
                    params[f"update_{field}"] = update_data[field].isoformat()
                else:
                    set_clauses.append(f"m.{field} = $update_{field}")
                    params[f"update_{field}"] = update_data[field]

        # Handle list fields
        list_fields = ["strengths", "challenges"]
        for field in list_fields:
            if field in update_data:
                set_clauses.append(f"m.{field} = $update_{field}")
                params[f"update_{field}"] = update_data[field]

        # Always update updated_at
        set_clauses.append("m.updated_at = datetime($now)")
        params["now"] = datetime.now().isoformat()

        if set_clauses:
            query = f"""
            MATCH (m:MonitoringRecord {{monitoring_id: $monitoring_id}})
            SET {', '.join(set_clauses)}
            RETURN m
            """

            result = tx.run(query, **params)
            record = result.single()

            if not record:
                raise Exception(f"Monitoring record {monitoring_id} not found")

            monitoring_node = dict(record["m"])

        # Update goal evaluations if provided
        if "goal_evaluations" in update_data:
            # Delete existing evaluations
            tx.run("""
                MATCH (m:MonitoringRecord {monitoring_id: $monitoring_id})-[r:EVALUATES]->()
                DELETE r
            """, monitoring_id=monitoring_id)

            # Create new evaluations
            for goal_eval in update_data["goal_evaluations"]:
                tx.run("""
                    MATCH (m:MonitoringRecord {monitoring_id: $monitoring_id})
                    MATCH (g:Goal {goal_id: $goal_id})
                    CREATE (m)-[:EVALUATES {
                        achievement_rate: $achievement_rate,
                        evaluation_comment: $evaluation_comment,
                        achievement_status: $achievement_status,
                        evidence: $evidence,
                        next_action: $next_action
                    }]->(g)
                """,
                       monitoring_id=monitoring_id,
                       goal_id=goal_eval["goal_id"],
                       achievement_rate=goal_eval["achievement_rate"],
                       evaluation_comment=goal_eval["evaluation_comment"],
                       achievement_status=goal_eval["achievement_status"],
                       evidence=goal_eval.get("evidence"),
                       next_action=goal_eval.get("next_action"))

        # Update service evaluations, new goals, service changes
        if "service_evaluations" in update_data:
            tx.run("""
                MATCH (m:MonitoringRecord {monitoring_id: $monitoring_id})
                SET m.service_evaluations = $service_evaluations
            """,
                   monitoring_id=monitoring_id,
                   service_evaluations=update_data["service_evaluations"])

        if "new_goals" in update_data:
            tx.run("""
                MATCH (m:MonitoringRecord {monitoring_id: $monitoring_id})
                SET m.new_goals = $new_goals
            """,
                   monitoring_id=monitoring_id,
                   new_goals=update_data["new_goals"])

        if "service_changes" in update_data:
            tx.run("""
                MATCH (m:MonitoringRecord {monitoring_id: $monitoring_id})
                SET m.service_changes = $service_changes
            """,
                   monitoring_id=monitoring_id,
                   service_changes=update_data["service_changes"])

        # Get complete updated record
        return MonitoringService._get_monitoring_record_tx(tx, monitoring_id)

    def delete_monitoring_record(self, monitoring_id: str) -> bool:
        """
        Delete monitoring record.

        Args:
            monitoring_id: Monitoring record ID

        Returns:
            True if deleted successfully
        """
        with self.driver.session(database=self.database) as session:
            result = session.execute_write(
                self._delete_monitoring_record_tx,
                monitoring_id
            )

        logger.info(f"Deleted monitoring record: {monitoring_id}")
        return result

    @staticmethod
    def _delete_monitoring_record_tx(tx, monitoring_id: str):
        """Transaction: Delete monitoring record."""

        query = """
        MATCH (m:MonitoringRecord {monitoring_id: $monitoring_id})
        OPTIONAL MATCH (m)-[r:EVALUATES]->()
        DELETE r, m
        RETURN count(m) as deleted_count
        """

        result = tx.run(query, monitoring_id=monitoring_id)
        record = result.single()

        return record["deleted_count"] > 0

    def get_progress_timeline(self, plan_id: str) -> List[Dict[str, Any]]:
        """
        Get progress timeline for all goals in a plan.

        Args:
            plan_id: Plan ID

        Returns:
            List of timeline data for each goal
        """
        query = """
        MATCH (p:Plan {plan_id: $plan_id})-[:HAS_GOAL]->(g:Goal)
        MATCH (p)-[:HAS_MONITORING]->(m:MonitoringRecord)-[r:EVALUATES]->(g)
        RETURN g.goal_id as goal_id,
               g.goal_text as goal_text,
               g.goal_type as goal_type,
               collect({
                   date: m.monitoring_date,
                   achievement_rate: r.achievement_rate,
                   comment: r.evaluation_comment,
                   status: r.achievement_status
               }) as timeline
        ORDER BY g.goal_type, g.goal_id
        """

        results = self.db.execute_read(query, {"plan_id": plan_id})
        timelines = []

        for record in results:
            timeline_data = dict(record)
            # Convert Neo4j datetime objects to Python datetime in timeline
            for item in timeline_data.get("timeline", []):
                if "date" in item and hasattr(item["date"], "to_native"):
                    item["date"] = item["date"].to_native()
            # Sort timeline by date
            timeline_data["timeline"] = sorted(
                timeline_data["timeline"],
                key=lambda x: x["date"]
            )
            timelines.append(timeline_data)

        return timelines


def get_monitoring_service() -> MonitoringService:
    """Get monitoring service instance."""
    return MonitoringService()
