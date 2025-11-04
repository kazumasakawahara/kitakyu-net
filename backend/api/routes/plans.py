# -*- coding: utf-8 -*-
"""
Plan API routes.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from loguru import logger

from backend.api.models.plan import Plan, PlanCreate, PlanUpdate
from backend.services.plan_service import get_plan_service
from backend.services.document_generator import get_document_generator
from backend.services.user_service import get_user_service

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("", response_model=Plan, status_code=201)
async def create_plan(plan_data: PlanCreate):
    """Create new service plan."""
    try:
        service = get_plan_service()

        # Convert Pydantic model to dict
        plan_dict = plan_data.model_dump()

        plan = service.create_plan(plan_dict)
        return plan
    except Exception as e:
        logger.error(f"Error creating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plan_id}", response_model=Plan)
async def get_plan(plan_id: str):
    """Get plan by ID."""
    try:
        service = get_plan_service()
        plan = service.get_plan(plan_id)

        if not plan:
            raise HTTPException(
                status_code=404, detail=f"Plan {plan_id} not found"
            )

        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=List[Plan])
async def get_user_plans(user_id: str):
    """Get all plans for a user."""
    try:
        service = get_plan_service()
        plans = service.list_plans_by_user(user_id)
        return plans
    except Exception as e:
        logger.error(f"Error getting plans for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{plan_id}", response_model=Plan)
async def update_plan(plan_id: str, update_data: PlanUpdate):
    """Update plan fields."""
    try:
        service = get_plan_service()

        # Convert Pydantic model to dict, excluding None values
        update_dict = update_data.model_dump(exclude_none=True)

        plan = service.update_plan(plan_id, update_dict)
        return plan
    except Exception as e:
        logger.error(f"Error updating plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plan_id}/pdf")
async def export_plan_pdf(plan_id: str):
    """Export plan as PDF."""
    try:
        plan_service = get_plan_service()
        user_service = get_user_service()
        doc_generator = get_document_generator()

        # Get plan data
        plan = plan_service.get_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")

        # Get user data
        user = user_service.get_user(plan["user_id"])
        if not user:
            raise HTTPException(status_code=404, detail=f"User {plan['user_id']} not found")

        # Generate PDF
        pdf_buffer = doc_generator.generate_pdf(plan, user)

        # Return as streaming response
        filename = f"plan_{plan_id}_{plan['user_id']}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting plan {plan_id} to PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plan_id}/word")
async def export_plan_word(plan_id: str):
    """Export plan as Word document."""
    try:
        plan_service = get_plan_service()
        user_service = get_user_service()
        doc_generator = get_document_generator()

        # Get plan data
        plan = plan_service.get_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")

        # Get user data
        user = user_service.get_user(plan["user_id"])
        if not user:
            raise HTTPException(status_code=404, detail=f"User {plan['user_id']} not found")

        # Generate Word document
        word_buffer = doc_generator.generate_word(plan, user)

        # Return as streaming response
        filename = f"plan_{plan_id}_{plan['user_id']}.docx"
        return StreamingResponse(
            word_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting plan {plan_id} to Word: {e}")
        raise HTTPException(status_code=500, detail=str(e))
