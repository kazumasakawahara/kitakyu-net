# -*- coding: utf-8 -*-
"""
Plan management service.

Handles CRUD operations for care plans with goals and service coordination.
"""
import uuid
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from loguru import logger

from backend.neo4j.client import get_neo4j_client


class PlanService:
    """Service for managing care plans."""

    def __init__(self):
        """Initialize plan service."""
        self.db = get_neo4j_client()
        logger.info("Plan service initialized")

    def create_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new care plan with goals.

        Args:
            plan_data: Plan data dict with user_id, assessment_id, goals, services

        Returns:
            Created plan dict with plan_id
        """
        plan_id = str(uuid.uuid4())
        now = datetime.now()

        # Extract data
        user_id = plan_data.get("user_id")
        assessment_id = plan_data.get("assessment_id")
        long_term_goals = plan_data.get("long_term_goals", [])
        short_term_goals = plan_data.get("short_term_goals", [])
        services = plan_data.get("services", [])
        plan_type = plan_data.get("plan_type", "個別支援計画")
        status = plan_data.get("status", "draft")

        logger.info(f"Creating plan for user: {user_id}, assessment: {assessment_id}")

        # Create plan node
        query = """
        MATCH (u:User {user_id: $user_id})
        OPTIONAL MATCH (a:Assessment {assessment_id: $assessment_id})
        CREATE (p:Plan {
            plan_id: $plan_id,
            user_id: $user_id,
            assessment_id: $assessment_id,
            plan_type: $plan_type,
            status: $status,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at)
        })
        CREATE (u)-[:HAS_PLAN]->(p)
        FOREACH (_ IN CASE WHEN a IS NOT NULL THEN [1] ELSE [] END |
            CREATE (p)-[:BASED_ON]->(a)
        )
        RETURN p
        """

        params = {
            "plan_id": plan_id,
            "user_id": user_id,
            "assessment_id": assessment_id,
            "plan_type": plan_type,
            "status": status,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        try:
            result = self.db.execute_write(query, params)
            if not result:
                raise Exception("Failed to create plan node")

            # Create long-term goals
            for idx, goal_data in enumerate(long_term_goals):
                self._create_goal_node(
                    plan_id, goal_data, goal_type="長期目標", order=idx
                )

            # Create short-term goals
            for idx, goal_data in enumerate(short_term_goals):
                self._create_goal_node(
                    plan_id, goal_data, goal_type="短期目標", order=idx
                )

            # Create service relationships
            for idx, service_data in enumerate(services):
                self._create_service_relationship(plan_id, service_data, order=idx)

            # Fetch complete plan
            created_plan = self.get_plan(plan_id)
            logger.success(f"Created plan: {plan_id}")
            return created_plan

        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            raise

    def _create_goal_node(
        self, plan_id: str, goal_data: Dict[str, Any], goal_type: str, order: int
    ) -> None:
        """Create goal node and link to plan."""
        goal_id = str(uuid.uuid4())
        now = datetime.now()

        query = """
        MATCH (p:Plan {plan_id: $plan_id})
        CREATE (g:Goal {
            goal_id: $goal_id,
            plan_id: $plan_id,
            goal_type: $goal_type,
            goal_text: $goal_text,
            evaluation_period: $evaluation_period,
            evaluation_criteria: $evaluation_criteria,
            goal_order: $goal_order,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at)
        })
        CREATE (p)-[:HAS_GOAL]->(g)
        RETURN g
        """

        params = {
            "plan_id": plan_id,
            "goal_id": goal_id,
            "goal_type": goal_type,
            "goal_text": goal_data.get("goal", ""),
            "evaluation_period": goal_data.get("period", ""),
            "evaluation_criteria": goal_data.get("criteria", ""),
            "goal_order": order,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        try:
            result = self.db.execute_write(query, params)
            if not result:
                logger.warning(f"Failed to create goal for plan: {plan_id}")
        except Exception as e:
            logger.error(f"Error creating goal: {e}")
            raise

    def _create_service_relationship(
        self, plan_id: str, service_data: Dict[str, Any], order: int
    ) -> None:
        """Create service coordination relationship."""
        # This will be implemented when facility nodes are available
        # For now, store service data as plan properties
        pass

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get plan by ID with all goals.

        Args:
            plan_id: Plan ID

        Returns:
            Plan dict with goals or None if not found
        """
        query = """
        MATCH (p:Plan {plan_id: $plan_id})
        OPTIONAL MATCH (p)-[:HAS_GOAL]->(g:Goal)
        WITH p, collect(g) as goals
        RETURN p, goals
        """

        try:
            result = self.db.execute_read(query, {"plan_id": plan_id})
            if not result:
                return None

            plan_node = result[0]["p"]
            goals = result[0]["goals"]

            plan = self._format_plan(dict(plan_node))

            # Organize goals by type
            long_term_goals = []
            short_term_goals = []

            for goal in goals:
                goal_dict = dict(goal)
                formatted_goal = self._format_goal(goal_dict)

                if goal_dict.get("goal_type") == "長期目標":
                    long_term_goals.append(formatted_goal)
                elif goal_dict.get("goal_type") == "短期目標":
                    short_term_goals.append(formatted_goal)

            # Sort by order
            long_term_goals.sort(key=lambda x: x.get("goal_order", 0))
            short_term_goals.sort(key=lambda x: x.get("goal_order", 0))

            plan["long_term_goals"] = long_term_goals
            plan["short_term_goals"] = short_term_goals
            plan["services"] = []  # Will be populated when facility integration is complete

            return plan

        except Exception as e:
            logger.error(f"Error getting plan {plan_id}: {e}")
            raise

    def list_plans_by_user(
        self, user_id: str, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all plans for a user.

        Args:
            user_id: User ID
            status: Optional status filter (draft, active, completed)

        Returns:
            List of plan dicts
        """
        conditions = ["p.user_id = $user_id"]
        params = {"user_id": user_id}

        if status:
            conditions.append("p.status = $status")
            params["status"] = status

        where_clause = " AND ".join(conditions)

        query = f"""
        MATCH (u:User {{user_id: $user_id}})-[:HAS_PLAN]->(p:Plan)
        WHERE {where_clause}
        OPTIONAL MATCH (p)-[:HAS_GOAL]->(g:Goal)
        WITH p, count(g) as goal_count
        RETURN p, goal_count
        ORDER BY p.created_at DESC
        """

        try:
            result = self.db.execute_write(query, params)
            plans = []

            for record in result:
                plan_node = record["p"]
                goal_count = record["goal_count"]

                plan = self._format_plan(dict(plan_node))
                plan["goal_count"] = goal_count
                plans.append(plan)

            logger.info(f"Found {len(plans)} plans for user {user_id}")
            return plans

        except Exception as e:
            logger.error(f"Error listing plans for user {user_id}: {e}")
            raise

    def update_plan(
        self, plan_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update plan fields.

        Args:
            plan_id: Plan ID
            update_data: Fields to update

        Returns:
            Updated plan dict
        """
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if not update_data:
            return self.get_plan(plan_id)

        # Build SET clause
        set_clauses = ["p.updated_at = datetime($updated_at)"]
        params = {"plan_id": plan_id, "updated_at": datetime.now().isoformat()}

        for key in ["status", "plan_type"]:
            if key in update_data:
                set_clauses.append(f"p.{key} = ${key}")
                params[key] = update_data[key]

        query = f"""
        MATCH (p:Plan {{plan_id: $plan_id}})
        SET {', '.join(set_clauses)}
        RETURN p
        """

        try:
            result = self.db.execute_write(query, params)
            if not result:
                raise Exception(f"Plan {plan_id} not found")

            logger.success(f"Updated plan: {plan_id}")
            return self.get_plan(plan_id)

        except Exception as e:
            logger.error(f"Error updating plan {plan_id}: {e}")
            raise

    def delete_plan(self, plan_id: str) -> bool:
        """
        Soft delete plan (mark as deleted).

        Args:
            plan_id: Plan ID

        Returns:
            True if deleted, False if not found
        """
        query = """
        MATCH (p:Plan {plan_id: $plan_id})
        SET p.status = 'deleted',
            p.deleted_at = datetime($deleted_at)
        RETURN p
        """

        params = {"plan_id": plan_id, "deleted_at": datetime.now().isoformat()}

        try:
            result = self.db.execute_write(query, params)
            if result:
                logger.success(f"Deleted plan: {plan_id}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Error deleting plan {plan_id}: {e}")
            raise

    def _format_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Format plan for API response."""
        # Convert Neo4j DateTime to ISO string
        if "created_at" in plan:
            plan["created_at"] = (
                plan["created_at"].iso_format()
                if hasattr(plan["created_at"], "iso_format")
                else str(plan["created_at"])
            )
        if "updated_at" in plan:
            plan["updated_at"] = (
                plan["updated_at"].iso_format()
                if hasattr(plan["updated_at"], "iso_format")
                else str(plan["updated_at"])
            )

        return plan

    def _format_goal(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Format goal for API response."""
        # Convert Neo4j DateTime to ISO string
        if "created_at" in goal:
            goal["created_at"] = (
                goal["created_at"].iso_format()
                if hasattr(goal["created_at"], "iso_format")
                else str(goal["created_at"])
            )
        if "updated_at" in goal:
            goal["updated_at"] = (
                goal["updated_at"].iso_format()
                if hasattr(goal["updated_at"], "iso_format")
                else str(goal["updated_at"])
            )

        return goal


# Global service instance
_plan_service = None


def get_plan_service() -> PlanService:
    """Get or create plan service instance."""
    global _plan_service
    if _plan_service is None:
        _plan_service = PlanService()
    return _plan_service
