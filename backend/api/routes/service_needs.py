# -*- coding: utf-8 -*-
"""
ServiceNeed API routes.
"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from backend.api.models.service_need import (
    ServiceNeed,
    ServiceNeedCreate,
    ServiceNeedUpdate,
    ServiceSuggestionRequest,
    ServiceSuggestionResponse,
    ServiceSuggestion,
    FacilityMatchRequest,
    FacilityMatchResponse,
    FacilityMatch,
)
from backend.services.service_need_service import get_service_need_service

router = APIRouter(prefix="/service-needs", tags=["service-needs"])


@router.post("", response_model=ServiceNeed, status_code=201)
async def create_service_need(service_data: ServiceNeedCreate):
    """Create new service need linked to plan."""
    try:
        service = get_service_need_service()
        service_need = service.create_service_need(service_data.model_dump())
        return service_need
    except Exception as e:
        logger.error(f"Error creating service need: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{service_need_id}", response_model=ServiceNeed)
async def get_service_need(service_need_id: str):
    """Get service need by ID."""
    try:
        service = get_service_need_service()
        service_need = service.get_service_need(service_need_id)

        if not service_need:
            raise HTTPException(
                status_code=404, detail=f"Service need {service_need_id} not found"
            )

        return service_need
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service need {service_need_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{service_need_id}", response_model=ServiceNeed)
async def update_service_need(service_need_id: str, update_data: ServiceNeedUpdate):
    """Update service need fields."""
    try:
        service = get_service_need_service()
        update_dict = update_data.model_dump(exclude_none=True)
        service_need = service.update_service_need(service_need_id, update_dict)
        return service_need
    except Exception as e:
        logger.error(f"Error updating service need {service_need_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest", response_model=ServiceSuggestionResponse)
async def suggest_services(request: ServiceSuggestionRequest):
    """Suggest services based on user needs and goals using LLM."""
    try:
        service = get_service_need_service()
        suggestions = service.suggest_services_for_user(
            user_id=request.user_id,
            assessment_id=request.assessment_id,
            goal_ids=request.goal_ids,
        )

        # Convert to response format
        service_suggestions = [
            ServiceSuggestion(**suggestion) for suggestion in suggestions
        ]

        return ServiceSuggestionResponse(
            user_id=request.user_id, suggestions=service_suggestions
        )
    except Exception as e:
        logger.error(f"Error suggesting services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match-facilities", response_model=FacilityMatchResponse)
async def match_facilities(request: FacilityMatchRequest):
    """Find and rank facilities that match service requirements using LLM."""
    try:
        service = get_service_need_service()
        matched_facilities = service.match_facilities_for_service(
            user_id=request.user_id,
            assessment_id=request.assessment_id,
            service_type=request.service_type,
            limit=request.limit,
        )

        # Convert to response format
        facility_matches = [
            FacilityMatch(**facility) for facility in matched_facilities
        ]

        return FacilityMatchResponse(
            service_type=request.service_type, matched_facilities=facility_matches
        )
    except Exception as e:
        logger.error(f"Error matching facilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))
