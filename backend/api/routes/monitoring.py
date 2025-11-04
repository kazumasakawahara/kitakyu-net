# -*- coding: utf-8 -*-
"""
Monitoring API routes.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from loguru import logger

from backend.api.models.monitoring import (
    MonitoringRecord,
    MonitoringCreate,
    MonitoringUpdate,
    ProgressTimeline
)
from backend.services.monitoring_service import get_monitoring_service
from backend.services.document_generator import get_document_generator
from backend.services.plan_service import get_plan_service
from backend.services.user_service import get_user_service

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.post("/plans/{plan_id}/monitoring", response_model=MonitoringRecord, status_code=201)
async def create_monitoring_record(plan_id: str, record_data: MonitoringCreate):
    """Create new monitoring record."""
    try:
        service = get_monitoring_service()

        # Verify plan exists
        plan_service = get_plan_service()
        plan = plan_service.get_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")

        # Ensure plan_id matches
        record_dict = record_data.model_dump()
        if record_dict["plan_id"] != plan_id:
            raise HTTPException(
                status_code=400,
                detail="plan_id in URL must match plan_id in request body"
            )

        # Convert nested models to dicts
        if "goal_evaluations" in record_dict:
            record_dict["goal_evaluations"] = [
                eval_item if isinstance(eval_item, dict) else eval_item.model_dump()
                for eval_item in record_dict["goal_evaluations"]
            ]

        if "service_evaluations" in record_dict:
            record_dict["service_evaluations"] = [
                eval_item if isinstance(eval_item, dict) else eval_item.model_dump()
                for eval_item in record_dict["service_evaluations"]
            ]

        if "new_goals" in record_dict:
            record_dict["new_goals"] = [
                goal if isinstance(goal, dict) else goal.model_dump()
                for goal in record_dict["new_goals"]
            ]

        if "service_changes" in record_dict:
            record_dict["service_changes"] = [
                change if isinstance(change, dict) else change.model_dump()
                for change in record_dict["service_changes"]
            ]

        record = service.create_monitoring_record(record_dict)
        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating monitoring record: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/{plan_id}/monitoring", response_model=List[MonitoringRecord])
async def list_monitoring_records(plan_id: str):
    """List all monitoring records for a plan."""
    try:
        service = get_monitoring_service()
        records = service.list_monitoring_records_by_plan(plan_id)
        return records

    except Exception as e:
        logger.error(f"Error listing monitoring records for plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{monitoring_id}", response_model=MonitoringRecord)
async def get_monitoring_record(monitoring_id: str):
    """Get monitoring record by ID."""
    try:
        service = get_monitoring_service()
        record = service.get_monitoring_record(monitoring_id)

        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"Monitoring record {monitoring_id} not found"
            )

        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monitoring record {monitoring_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{monitoring_id}", response_model=MonitoringRecord)
async def update_monitoring_record(monitoring_id: str, update_data: MonitoringUpdate):
    """Update monitoring record."""
    try:
        service = get_monitoring_service()

        # Convert Pydantic model to dict, excluding None values
        update_dict = update_data.model_dump(exclude_none=True)

        # Convert nested models to dicts
        if "goal_evaluations" in update_dict:
            update_dict["goal_evaluations"] = [
                eval_item if isinstance(eval_item, dict) else eval_item.model_dump()
                for eval_item in update_dict["goal_evaluations"]
            ]

        if "service_evaluations" in update_dict:
            update_dict["service_evaluations"] = [
                eval_item if isinstance(eval_item, dict) else eval_item.model_dump()
                for eval_item in update_dict["service_evaluations"]
            ]

        if "new_goals" in update_dict:
            update_dict["new_goals"] = [
                goal if isinstance(goal, dict) else goal.model_dump()
                for goal in update_dict["new_goals"]
            ]

        if "service_changes" in update_dict:
            update_dict["service_changes"] = [
                change if isinstance(change, dict) else change.model_dump()
                for change in update_dict["service_changes"]
            ]

        record = service.update_monitoring_record(monitoring_id, update_dict)
        return record

    except Exception as e:
        logger.error(f"Error updating monitoring record {monitoring_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{monitoring_id}")
async def delete_monitoring_record(monitoring_id: str):
    """Delete monitoring record."""
    try:
        service = get_monitoring_service()
        success = service.delete_monitoring_record(monitoring_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Monitoring record {monitoring_id} not found"
            )

        return {"message": f"Monitoring record {monitoring_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting monitoring record {monitoring_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/{plan_id}/progress", response_model=List[ProgressTimeline])
async def get_progress_timeline(plan_id: str):
    """Get progress timeline for all goals in a plan."""
    try:
        service = get_monitoring_service()
        timeline = service.get_progress_timeline(plan_id)
        return timeline

    except Exception as e:
        logger.error(f"Error getting progress timeline for plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{monitoring_id}/pdf")
async def export_monitoring_pdf(monitoring_id: str):
    """Export monitoring record as PDF."""
    try:
        monitoring_service = get_monitoring_service()
        plan_service = get_plan_service()
        user_service = get_user_service()
        doc_generator = get_document_generator()

        # Get monitoring record
        record = monitoring_service.get_monitoring_record(monitoring_id)
        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"Monitoring record {monitoring_id} not found"
            )

        # Get plan data
        plan = plan_service.get_plan(record["plan_id"])
        if not plan:
            raise HTTPException(
                status_code=404,
                detail=f"Plan {record['plan_id']} not found"
            )

        # Get user data
        user = user_service.get_user(plan["user_id"])
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {plan['user_id']} not found"
            )

        # Generate monitoring-specific PDF
        pdf_buffer = doc_generator.generate_monitoring_pdf(record, plan, user)

        # Return as streaming response
        filename = f"monitoring_{monitoring_id}_{record['monitoring_date']}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting monitoring {monitoring_id} to PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{monitoring_id}/word")
async def export_monitoring_word(monitoring_id: str):
    """Export monitoring record as Word document."""
    try:
        monitoring_service = get_monitoring_service()
        plan_service = get_plan_service()
        user_service = get_user_service()
        doc_generator = get_document_generator()

        # Get monitoring record
        record = monitoring_service.get_monitoring_record(monitoring_id)
        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"Monitoring record {monitoring_id} not found"
            )

        # Get plan data
        plan = plan_service.get_plan(record["plan_id"])
        if not plan:
            raise HTTPException(
                status_code=404,
                detail=f"Plan {record['plan_id']} not found"
            )

        # Get user data
        user = user_service.get_user(plan["user_id"])
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {plan['user_id']} not found"
            )

        # Generate monitoring-specific Word document
        word_buffer = doc_generator.generate_monitoring_word(record, plan, user)

        # Return as streaming response
        filename = f"monitoring_{monitoring_id}_{record['monitoring_date']}.docx"
        return StreamingResponse(
            word_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting monitoring {monitoring_id} to Word: {e}")
        raise HTTPException(status_code=500, detail=str(e))
