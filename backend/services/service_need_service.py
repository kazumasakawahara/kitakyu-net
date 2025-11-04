# -*- coding: utf-8 -*-
"""
Service need management service.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from loguru import logger

from backend.neo4j.client import get_neo4j_client
from backend.llm.service_coordinator import get_service_coordinator
from backend.services.user_service import get_user_service
from backend.services.assessment_service import get_assessment_service
from backend.services.goal_service import get_goal_service


class ServiceNeedService:
    """Service for managing service needs."""

    def __init__(self):
        """Initialize service need service."""
        self.db = get_neo4j_client()
        self.coordinator = get_service_coordinator()
        self.user_service = get_user_service()
        self.assessment_service = get_assessment_service()
        self.goal_service = get_goal_service()

    def create_service_need(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new service need linked to plan."""
        service_need_id = str(uuid.uuid4())
        now = datetime.now()

        query = """
        MATCH (p:Plan {plan_id: $plan_id})
        CREATE (s:ServiceNeed {
            service_need_id: $service_need_id,
            plan_id: $plan_id,
            service_type: $service_type,
            frequency: $frequency,
            priority: $priority,
            reason: $reason,
            duration_hours: $duration_hours,
            preferred_time: $preferred_time,
            special_requirements: $special_requirements,
            goal_id: $goal_id,
            facility_id: $facility_id,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at)
        })
        CREATE (p)-[:INCLUDES_SERVICE]->(s)
        RETURN s
        """

        params = {
            "service_need_id": service_need_id,
            "plan_id": service_data["plan_id"],
            "service_type": service_data["service_type"],
            "frequency": service_data["frequency"],
            "priority": service_data["priority"],
            "reason": service_data["reason"],
            "duration_hours": service_data.get("duration_hours"),
            "preferred_time": service_data.get("preferred_time"),
            "special_requirements": service_data.get("special_requirements"),
            "goal_id": service_data.get("goal_id"),
            "facility_id": service_data.get("facility_id"),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        try:
            result = self.db.execute_query(query, params)
            if result:
                service_node = result[0]["s"]
                created_service = self._format_service_need(dict(service_node))
                logger.success(f"Created service need: {service_need_id}")
                return created_service
            else:
                raise Exception("Failed to create service need")

        except Exception as e:
            logger.error(f"Error creating service need: {e}")
            raise

    def get_service_need(self, service_need_id: str) -> Optional[Dict[str, Any]]:
        """Get service need by ID."""
        query = """
        MATCH (s:ServiceNeed {service_need_id: $service_need_id})
        OPTIONAL MATCH (s)<-[:PROVIDED_BY]-(f:Facility)
        RETURN s, f.name AS facility_name
        """

        try:
            result = self.db.execute_query(query, {"service_need_id": service_need_id})
            if result:
                service_node = result[0]["s"]
                service = self._format_service_need(dict(service_node))
                service["facility_name"] = result[0].get("facility_name")
                return service
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting service need {service_need_id}: {e}")
            raise

    def update_service_need(
        self, service_need_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update service need fields."""
        now = datetime.now()

        # Build SET clause dynamically
        set_clauses = ["s.updated_at = datetime($updated_at)"]
        params = {"service_need_id": service_need_id, "updated_at": now.isoformat()}

        for field in [
            "frequency",
            "priority",
            "duration_hours",
            "preferred_time",
            "special_requirements",
            "facility_id",
        ]:
            if field in update_data:
                set_clauses.append(f"s.{field} = ${field}")
                params[field] = update_data[field]

        query = f"""
        MATCH (s:ServiceNeed {{service_need_id: $service_need_id}})
        SET {', '.join(set_clauses)}
        RETURN s
        """

        try:
            result = self.db.execute_query(query, params)
            if result:
                service_node = result[0]["s"]
                updated_service = self._format_service_need(dict(service_node))
                logger.success(f"Updated service need: {service_need_id}")
                return updated_service
            else:
                raise Exception(f"Service need {service_need_id} not found")

        except Exception as e:
            logger.error(f"Error updating service need {service_need_id}: {e}")
            raise

    def suggest_services_for_user(
        self, user_id: str, assessment_id: str, goal_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate service suggestions based on user, assessment, and goals."""
        logger.info(
            f"Suggesting services for user: {user_id}, goals: {goal_ids}"
        )

        # Get user data
        user = self.user_service.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Get assessment data
        assessment = self.assessment_service.get_assessment(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # Get goals
        goals = []
        for goal_id in goal_ids:
            goal = self.goal_service.get_goal(goal_id)
            if goal:
                goals.append(goal)

        if not goals:
            raise ValueError("No valid goals provided")

        # Generate suggestions using LLM
        try:
            suggestions = self.coordinator.suggest_services(
                user_data=user, assessment_data=assessment, goals=goals
            )
            logger.success(f"Generated {len(suggestions)} service suggestions")
            return suggestions

        except Exception as e:
            logger.error(f"Service suggestion failed: {e}")
            raise

    def match_facilities_for_service(
        self, user_id: str, assessment_id: str, service_type: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find and rank facilities that match service requirements."""
        logger.info(
            f"Matching facilities for user: {user_id}, service: {service_type}"
        )

        # Get user data
        user = self.user_service.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Get assessment data
        assessment = self.assessment_service.get_assessment(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # Match facilities using LLM
        try:
            matched_facilities = self.coordinator.match_facilities(
                service_type=service_type,
                user_data=user,
                assessment_data=assessment,
                limit=limit,
            )
            logger.success(f"Matched {len(matched_facilities)} facilities")
            return matched_facilities

        except Exception as e:
            logger.error(f"Facility matching failed: {e}")
            raise

    def _format_service_need(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Format service need for API response."""
        # Convert Neo4j DateTime to ISO string
        if "created_at" in service:
            service["created_at"] = (
                service["created_at"].iso_format()
                if hasattr(service["created_at"], "iso_format")
                else str(service["created_at"])
            )
        if "updated_at" in service:
            service["updated_at"] = (
                service["updated_at"].iso_format()
                if hasattr(service["updated_at"], "iso_format")
                else str(service["updated_at"])
            )

        # Ensure optional fields exist
        if "facility_name" not in service:
            service["facility_name"] = None
        if "goal_id" not in service:
            service["goal_id"] = None
        if "facility_id" not in service:
            service["facility_id"] = None

        return service


# Global service instance
_service_need_service = None


def get_service_need_service() -> ServiceNeedService:
    """Get or create service need service instance."""
    global _service_need_service
    if _service_need_service is None:
        _service_need_service = ServiceNeedService()
    return _service_need_service
