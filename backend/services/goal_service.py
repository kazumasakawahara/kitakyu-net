# -*- coding: utf-8 -*-
"""
Goal management service.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from loguru import logger

from backend.neo4j.client import get_neo4j_client
from backend.llm.goal_generator import get_goal_generator
from backend.services.assessment_service import get_assessment_service


class GoalService:
    """Service for managing goals."""

    def __init__(self):
        """Initialize goal service."""
        self.db = get_neo4j_client()
        self.generator = get_goal_generator()
        self.assessment_service = get_assessment_service()

    def create_goal(self, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new goal linked to plan."""
        goal_id = str(uuid.uuid4())
        now = datetime.now()

        # Build SMART evaluation dict
        smart_eval = goal_data.get("smart_evaluation")
        smart_dict = {}
        if smart_eval:
            smart_dict = {
                "is_specific": smart_eval.get("is_specific", False),
                "is_measurable": smart_eval.get("is_measurable", False),
                "is_achievable": smart_eval.get("is_achievable", False),
                "is_relevant": smart_eval.get("is_relevant", False),
                "is_time_bound": smart_eval.get("is_time_bound", False),
            }

        query = """
        MATCH (p:Plan {plan_id: $plan_id})
        CREATE (g:Goal {
            goal_id: $goal_id,
            plan_id: $plan_id,
            goal_text: $goal_text,
            goal_type: $goal_type,
            goal_reason: $goal_reason,
            evaluation_period: $evaluation_period,
            evaluation_method: $evaluation_method,
            is_specific: $is_specific,
            is_measurable: $is_measurable,
            is_achievable: $is_achievable,
            is_relevant: $is_relevant,
            is_time_bound: $is_time_bound,
            confidence: $confidence,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at)
        })
        CREATE (p)-[:HAS_LONG_TERM_GOAL]->(g)
        RETURN g
        """

        params = {
            "goal_id": goal_id,
            "plan_id": goal_data["plan_id"],
            "goal_text": goal_data["goal_text"],
            "goal_type": goal_data["goal_type"],
            "goal_reason": goal_data.get("goal_reason"),
            "evaluation_period": goal_data.get("evaluation_period"),
            "evaluation_method": goal_data.get("evaluation_method"),
            "is_specific": smart_dict.get("is_specific", False),
            "is_measurable": smart_dict.get("is_measurable", False),
            "is_achievable": smart_dict.get("is_achievable", False),
            "is_relevant": smart_dict.get("is_relevant", False),
            "is_time_bound": smart_dict.get("is_time_bound", False),
            "confidence": goal_data.get("confidence"),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        try:
            result = self.db.execute_query(query, params)
            if result:
                goal_node = result[0]["g"]
                created_goal = self._format_goal(dict(goal_node))
                logger.success(f"Created goal: {goal_id}")
                return created_goal
            else:
                raise Exception("Failed to create goal")

        except Exception as e:
            logger.error(f"Error creating goal: {e}")
            raise

    def get_goal(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """Get goal by ID."""
        query = """
        MATCH (g:Goal {goal_id: $goal_id})
        RETURN g
        """

        try:
            result = self.db.execute_query(query, {"goal_id": goal_id})
            if result:
                goal_node = result[0]["g"]
                return self._format_goal(dict(goal_node))
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting goal {goal_id}: {e}")
            raise

    def update_goal(
        self, goal_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update goal fields."""
        now = datetime.now()

        # Build SET clause dynamically
        set_clauses = ["g.updated_at = datetime($updated_at)"]
        params = {"goal_id": goal_id, "updated_at": now.isoformat()}

        if "goal_text" in update_data:
            set_clauses.append("g.goal_text = $goal_text")
            params["goal_text"] = update_data["goal_text"]

        if "goal_reason" in update_data:
            set_clauses.append("g.goal_reason = $goal_reason")
            params["goal_reason"] = update_data["goal_reason"]

        if "evaluation_period" in update_data:
            set_clauses.append("g.evaluation_period = $evaluation_period")
            params["evaluation_period"] = update_data["evaluation_period"]

        if "evaluation_method" in update_data:
            set_clauses.append("g.evaluation_method = $evaluation_method")
            params["evaluation_method"] = update_data["evaluation_method"]

        if "confidence" in update_data:
            set_clauses.append("g.confidence = $confidence")
            params["confidence"] = update_data["confidence"]

        # Update SMART evaluation
        smart_eval = update_data.get("smart_evaluation")
        if smart_eval:
            for key in [
                "is_specific",
                "is_measurable",
                "is_achievable",
                "is_relevant",
                "is_time_bound",
            ]:
                if key in smart_eval:
                    set_clauses.append(f"g.{key} = ${key}")
                    params[key] = smart_eval[key]

        query = f"""
        MATCH (g:Goal {{goal_id: $goal_id}})
        SET {', '.join(set_clauses)}
        RETURN g
        """

        try:
            result = self.db.execute_query(query, params)
            if result:
                goal_node = result[0]["g"]
                updated_goal = self._format_goal(dict(goal_node))
                logger.success(f"Updated goal: {goal_id}")
                return updated_goal
            else:
                raise Exception(f"Goal {goal_id} not found")

        except Exception as e:
            logger.error(f"Error updating goal {goal_id}: {e}")
            raise

    def suggest_goals_for_assessment(
        self, assessment_id: str, goal_type: str = "長期目標"
    ) -> List[Dict[str, Any]]:
        """Generate goal suggestions based on assessment."""
        logger.info(
            f"Suggesting {goal_type} for assessment: {assessment_id}"
        )

        # Get assessment data
        assessment = self.assessment_service.get_assessment(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # Build assessment data dict
        # If structured fields are empty, use interview_content as fallback
        assessment_data = {
            "preferences": assessment.get("preferences", []),
            "analyzed_needs": assessment.get("analyzed_needs", []),
            "strengths": assessment.get("strengths", []),
            "challenges": assessment.get("challenges", []),
            "interview_content": assessment.get("interview_content", ""),
        }

        # Generate suggestions using LLM
        try:
            suggestions = self.generator.suggest_goals(
                assessment_data, goal_type=goal_type
            )
            logger.success(f"Generated {len(suggestions)} goal suggestions")
            return suggestions

        except Exception as e:
            logger.error(f"Goal suggestion failed: {e}")
            raise

    def evaluate_goal_smart(self, goal_text: str) -> Dict[str, Any]:
        """Evaluate goal against SMART criteria."""
        try:
            evaluation = self.generator.evaluate_goal_smart(goal_text)
            logger.success(f"SMART evaluation completed: {evaluation.get('smart_score')}")
            return evaluation

        except Exception as e:
            logger.error(f"SMART evaluation failed: {e}")
            raise

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

        # Build SMART evaluation dict
        smart_evaluation = None
        if any(
            key in goal
            for key in [
                "is_specific",
                "is_measurable",
                "is_achievable",
                "is_relevant",
                "is_time_bound",
            ]
        ):
            smart_evaluation = {
                "is_specific": goal.get("is_specific", False),
                "is_measurable": goal.get("is_measurable", False),
                "is_achievable": goal.get("is_achievable", False),
                "is_relevant": goal.get("is_relevant", False),
                "is_time_bound": goal.get("is_time_bound", False),
            }

        goal["smart_evaluation"] = smart_evaluation

        # Ensure confidence field exists (fix for validation error)
        if "confidence" not in goal:
            goal["confidence"] = None

        return goal


# Global service instance
_goal_service = None


def get_goal_service() -> GoalService:
    """Get or create goal service instance."""
    global _goal_service
    if _goal_service is None:
        _goal_service = GoalService()
    return _goal_service
