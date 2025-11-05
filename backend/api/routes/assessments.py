# -*- coding: utf-8 -*-
"""
Assessment API routes.
"""
from fastapi import APIRouter, HTTPException
from typing import List
from loguru import logger

from backend.api.models.assessment import (
    Assessment,
    AssessmentCreate,
    AnalyzeRequest,
    AnalyzeResponse,
    AssessmentAnalysis,
    ICFClassification,
)
from backend.services.assessment_service import get_assessment_service

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("", response_model=Assessment, status_code=201)
async def create_assessment(assessment_data: AssessmentCreate):
    """Create new assessment with optional LLM analysis."""
    try:
        service = get_assessment_service()
        assessment = service.create_assessment(
            assessment_data.model_dump(exclude={"analyze"}),
            analyze=assessment_data.analyze,
        )
        return assessment
    except Exception as e:
        logger.error(f"Error creating assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{assessment_id}", response_model=Assessment)
async def get_assessment(assessment_id: str):
    """Get assessment by ID."""
    try:
        service = get_assessment_service()
        assessment = service.get_assessment(assessment_id)

        if not assessment:
            raise HTTPException(
                status_code=404, detail=f"Assessment {assessment_id} not found"
            )

        return assessment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting assessment {assessment_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{assessment_id}/reanalyze", response_model=AnalyzeResponse)
async def reanalyze_assessment(assessment_id: str):
    """Re-analyze assessment with LLM."""
    try:
        service = get_assessment_service()
        assessment = service.reanalyze_assessment(assessment_id)

        # Build analysis response
        analysis = AssessmentAnalysis(
            analyzed_needs=assessment.get("analyzed_needs", []),
            strengths=assessment.get("strengths", []),
            challenges=assessment.get("challenges", []),
            preferences=assessment.get("preferences", []),
            family_wishes=assessment.get("family_wishes", []),
            icf_classification=ICFClassification(
                body_functions=assessment.get("body_functions", ""),
                activities=assessment.get("activities", ""),
                participation=assessment.get("participation", ""),
                environmental_factors=assessment.get("environmental_factors", ""),
                personal_factors=assessment.get("personal_factors", ""),
            ),
            confidence_score=assessment.get("confidence_score"),
        )

        return {
            "assessment_id": assessment_id,
            "analysis": analysis,
            "message": "Assessment re-analyzed successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error re-analyzing assessment {assessment_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=List[Assessment])
async def get_user_assessments(user_id: str):
    """Get all assessments for a user."""
    try:
        service = get_assessment_service()
        assessments = service.list_user_assessments(user_id)
        return assessments
    except Exception as e:
        logger.error(f"Error getting assessments for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/followup-questions")
async def generate_followup_questions(request: AnalyzeRequest):
    """Generate follow-up questions for incomplete assessment."""
    try:
        from backend.llm.needs_analyzer import get_needs_analyzer

        analyzer = get_needs_analyzer()
        questions_data = analyzer.generate_followup_questions(request.interview_content)

        return questions_data
    except Exception as e:
        logger.error(f"Error generating follow-up questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
