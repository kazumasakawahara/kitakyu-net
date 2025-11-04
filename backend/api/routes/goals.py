# -*- coding: utf-8 -*-
"""
Goal API routes.
"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from backend.api.models.goal import (
    Goal,
    GoalCreate,
    GoalUpdate,
    GoalSuggestionRequest,
    GoalSuggestionResponse,
    GoalSuggestion,
    SMARTEvaluationRequest,
    SMARTEvaluationResponse,
    SMARTEvaluation,
)
from backend.services.goal_service import get_goal_service

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("", response_model=Goal, status_code=201)
async def create_goal(goal_data: GoalCreate):
    """Create new goal linked to plan."""
    try:
        service = get_goal_service()

        # Convert Pydantic model to dict
        goal_dict = goal_data.model_dump()

        goal = service.create_goal(goal_dict)
        return goal
    except Exception as e:
        logger.error(f"Error creating goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{goal_id}", response_model=Goal)
async def get_goal(goal_id: str):
    """Get goal by ID."""
    try:
        service = get_goal_service()
        goal = service.get_goal(goal_id)

        if not goal:
            raise HTTPException(
                status_code=404, detail=f"Goal {goal_id} not found"
            )

        return goal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting goal {goal_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{goal_id}", response_model=Goal)
async def update_goal(goal_id: str, update_data: GoalUpdate):
    """Update goal fields."""
    try:
        service = get_goal_service()

        # Convert Pydantic model to dict, excluding None values
        update_dict = update_data.model_dump(exclude_none=True)

        goal = service.update_goal(goal_id, update_dict)
        return goal
    except Exception as e:
        logger.error(f"Error updating goal {goal_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest", response_model=GoalSuggestionResponse)
async def suggest_goals(request: GoalSuggestionRequest):
    """Suggest goals based on assessment using LLM."""
    try:
        service = get_goal_service()
        suggestions = service.suggest_goals_for_assessment(
            request.assessment_id, goal_type=request.goal_type
        )

        # Convert to response format
        goal_suggestions = []
        for suggestion in suggestions:
            smart_eval = suggestion.get("smart_evaluation", {})
            goal_suggestions.append(
                GoalSuggestion(
                    goal_text=suggestion["goal_text"],
                    goal_reason=suggestion.get("goal_reason", ""),
                    evaluation_period=suggestion.get("evaluation_period", ""),
                    evaluation_method=suggestion.get("evaluation_method", ""),
                    smart_evaluation=SMARTEvaluation(**smart_eval),
                    confidence=suggestion.get("confidence", 0.0),
                )
            )

        return GoalSuggestionResponse(
            assessment_id=request.assessment_id,
            goal_type=request.goal_type,
            suggestions=goal_suggestions,
        )
    except Exception as e:
        logger.error(f"Error suggesting goals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate", response_model=SMARTEvaluationResponse)
async def evaluate_goal_smart(request: SMARTEvaluationRequest):
    """Evaluate goal against SMART criteria using LLM."""
    try:
        service = get_goal_service()
        evaluation = service.evaluate_goal_smart(request.goal_text)

        return SMARTEvaluationResponse(
            goal_text=request.goal_text,
            is_specific=evaluation["is_specific"],
            is_measurable=evaluation["is_measurable"],
            is_achievable=evaluation["is_achievable"],
            is_relevant=evaluation["is_relevant"],
            is_time_bound=evaluation["is_time_bound"],
            smart_score=evaluation["smart_score"],
            suggestions=evaluation.get("suggestions", []),
        )
    except Exception as e:
        logger.error(f"Error evaluating goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))
