# -*- coding: utf-8 -*-
"""
Assessment management service.
"""
import uuid
import json
from datetime import datetime, date
from typing import Dict, Any, Optional
from loguru import logger

from backend.neo4j.client import get_neo4j_client
from backend.llm.needs_analyzer import get_needs_analyzer


class AssessmentService:
    """Service for managing assessments."""

    def __init__(self):
        """Initialize assessment service."""
        self.db = get_neo4j_client()
        self.analyzer = get_needs_analyzer()

    def create_assessment(
        self, assessment_data: Dict[str, Any], analyze: bool = False
    ) -> Dict[str, Any]:
        """Create new assessment with optional LLM analysis."""
        assessment_id = str(uuid.uuid4())
        now = datetime.now()

        # Convert date to ISO string
        if "interview_date" in assessment_data and isinstance(
            assessment_data["interview_date"], date
        ):
            assessment_data["interview_date"] = assessment_data[
                "interview_date"
            ].isoformat()

        # Perform LLM analysis if requested
        analysis = None
        if analyze and "interview_content" in assessment_data:
            try:
                analysis = self.analyzer.analyze(assessment_data["interview_content"])
                confidence = self.analyzer.calculate_confidence_score(analysis)
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                analysis = None
                confidence = None
        else:
            confidence = None

        # Build query
        query = """
        MATCH (u:User {user_id: $user_id})
        CREATE (a:Assessment {
            assessment_id: $assessment_id,
            user_id: $user_id,
            interview_date: date($interview_date),
            interview_participants: $interview_participants,
            interview_content: $interview_content,
            analyzed_needs: $analyzed_needs,
            strengths: $strengths,
            challenges: $challenges,
            preferences: $preferences,
            family_wishes: $family_wishes,
            body_functions: $body_functions,
            activities: $activities,
            participation: $participation,
            environmental_factors: $environmental_factors,
            personal_factors: $personal_factors,
            confidence_score: $confidence_score,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at)
        })
        CREATE (u)-[:HAS_ASSESSMENT]->(a)
        RETURN a
        """

        params = {
            "assessment_id": assessment_id,
            "user_id": assessment_data["user_id"],
            "interview_date": assessment_data["interview_date"],
            "interview_participants": assessment_data.get("interview_participants", ""),
            "interview_content": assessment_data["interview_content"],
            "analyzed_needs": analysis.get("analyzed_needs") if analysis else [],
            "strengths": analysis.get("strengths") if analysis else [],
            "challenges": analysis.get("challenges") if analysis else [],
            "preferences": analysis.get("preferences") if analysis else [],
            "family_wishes": analysis.get("family_wishes") if analysis else [],
            "body_functions": (
                analysis.get("icf_classification", {}).get("body_functions", "")
                if analysis
                else ""
            ),
            "activities": (
                analysis.get("icf_classification", {}).get("activities", "")
                if analysis
                else ""
            ),
            "participation": (
                analysis.get("icf_classification", {}).get("participation", "")
                if analysis
                else ""
            ),
            "environmental_factors": (
                analysis.get("icf_classification", {}).get("environmental_factors", "")
                if analysis
                else ""
            ),
            "personal_factors": (
                analysis.get("icf_classification", {}).get("personal_factors", "")
                if analysis
                else ""
            ),
            "confidence_score": confidence,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        try:
            result = self.db.execute_write(query, params)
            if result:
                assessment_node = result[0]["a"]
                created_assessment = dict(assessment_node)

                # Convert Neo4j types
                if "interview_date" in created_assessment:
                    created_assessment["interview_date"] = (
                        created_assessment["interview_date"].to_native().isoformat()
                    )
                if "created_at" in created_assessment:
                    created_assessment["created_at"] = (
                        created_assessment["created_at"].iso_format()
                        if hasattr(created_assessment["created_at"], "iso_format")
                        else str(created_assessment["created_at"])
                    )
                if "updated_at" in created_assessment:
                    created_assessment["updated_at"] = (
                        created_assessment["updated_at"].iso_format()
                        if hasattr(created_assessment["updated_at"], "iso_format")
                        else str(created_assessment["updated_at"])
                    )

                logger.success(f"Created assessment: {assessment_id}")
                return created_assessment
            else:
                raise Exception("Failed to create assessment")

        except Exception as e:
            logger.error(f"Error creating assessment: {e}")
            raise

    def reanalyze_assessment(
        self, assessment_id: str
    ) -> Dict[str, Any]:
        """Re-analyze existing assessment with LLM."""
        # Get assessment
        assessment = self.get_assessment(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # Perform analysis
        try:
            analysis = self.analyzer.analyze(
                assessment["interview_content"]
            )
            confidence = self.analyzer.calculate_confidence_score(analysis)
        except Exception as e:
            logger.error(f"Re-analysis failed: {e}")
            raise

        # Update assessment with new analysis
        query = """
        MATCH (a:Assessment {assessment_id: $assessment_id})
        SET a.analyzed_needs = $analyzed_needs,
            a.strengths = $strengths,
            a.challenges = $challenges,
            a.preferences = $preferences,
            a.family_wishes = $family_wishes,
            a.body_functions = $body_functions,
            a.activities = $activities,
            a.participation = $participation,
            a.environmental_factors = $environmental_factors,
            a.personal_factors = $personal_factors,
            a.confidence_score = $confidence_score,
            a.updated_at = datetime($updated_at)
        RETURN a
        """

        params = {
            "assessment_id": assessment_id,
            "analyzed_needs": analysis.get("analyzed_needs", []),
            "strengths": analysis.get("strengths", []),
            "challenges": analysis.get("challenges", []),
            "preferences": analysis.get("preferences", []),
            "family_wishes": analysis.get("family_wishes", []),
            "body_functions": analysis.get("icf_classification", {}).get(
                "body_functions", ""
            ),
            "activities": analysis.get("icf_classification", {}).get("activities", ""),
            "participation": analysis.get("icf_classification", {}).get(
                "participation", ""
            ),
            "environmental_factors": analysis.get("icf_classification", {}).get(
                "environmental_factors", ""
            ),
            "personal_factors": analysis.get("icf_classification", {}).get(
                "personal_factors", ""
            ),
            "confidence_score": confidence,
            "updated_at": datetime.now().isoformat(),
        }

        result = self.db.execute_write(query, params)
        if result:
            assessment_node = result[0]["a"]
            updated_assessment = dict(assessment_node)

            # Convert Neo4j types
            if "interview_date" in updated_assessment:
                updated_assessment["interview_date"] = (
                    updated_assessment["interview_date"].to_native().isoformat()
                )
            if "created_at" in updated_assessment:
                updated_assessment["created_at"] = (
                    updated_assessment["created_at"].iso_format()
                    if hasattr(updated_assessment["created_at"], "iso_format")
                    else str(updated_assessment["created_at"])
                )
            if "updated_at" in updated_assessment:
                updated_assessment["updated_at"] = (
                    updated_assessment["updated_at"].iso_format()
                    if hasattr(updated_assessment["updated_at"], "iso_format")
                    else str(updated_assessment["updated_at"])
                )

            logger.success(f"Re-analyzed assessment: {assessment_id}")
            return updated_assessment

    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get assessment by ID."""
        query = """
        MATCH (a:Assessment {assessment_id: $assessment_id})
        RETURN a
        """

        try:
            result = self.db.execute_read(query, {"assessment_id": assessment_id})
            if result:
                assessment_node = result[0]["a"]
                assessment = dict(assessment_node)

                # Convert Neo4j types
                if "interview_date" in assessment:
                    assessment["interview_date"] = (
                        assessment["interview_date"].to_native().isoformat()
                    )
                if "created_at" in assessment:
                    assessment["created_at"] = (
                        assessment["created_at"].iso_format()
                        if hasattr(assessment["created_at"], "iso_format")
                        else str(assessment["created_at"])
                    )
                if "updated_at" in assessment:
                    assessment["updated_at"] = (
                        assessment["updated_at"].iso_format()
                        if hasattr(assessment["updated_at"], "iso_format")
                        else str(assessment["updated_at"])
                    )

                return assessment
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting assessment {assessment_id}: {e}")
            raise

    def list_user_assessments(self, user_id: str) -> list[Dict[str, Any]]:
        """Get all assessments for a user."""
        query = """
        MATCH (u:User {user_id: $user_id})-[:HAS_ASSESSMENT]->(a:Assessment)
        RETURN a
        ORDER BY a.created_at DESC
        """

        try:
            result = self.db.execute_read(query, {"user_id": user_id})
            assessments = []

            for record in result:
                assessment_node = record["a"]
                assessment = dict(assessment_node)

                # Convert Neo4j types
                if "interview_date" in assessment:
                    assessment["interview_date"] = (
                        assessment["interview_date"].to_native().isoformat()
                    )
                if "created_at" in assessment:
                    assessment["created_at"] = (
                        assessment["created_at"].iso_format()
                        if hasattr(assessment["created_at"], "iso_format")
                        else str(assessment["created_at"])
                    )
                if "updated_at" in assessment:
                    assessment["updated_at"] = (
                        assessment["updated_at"].iso_format()
                        if hasattr(assessment["updated_at"], "iso_format")
                        else str(assessment["updated_at"])
                    )

                assessments.append(assessment)

            return assessments

        except Exception as e:
            logger.error(f"Error getting assessments for user {user_id}: {e}")
            raise


# Global service instance
_assessment_service = None


def get_assessment_service() -> AssessmentService:
    """Get or create assessment service instance."""
    global _assessment_service
    if _assessment_service is None:
        _assessment_service = AssessmentService()
    return _assessment_service
