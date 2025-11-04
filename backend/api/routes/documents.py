# -*- coding: utf-8 -*-
"""
Document generation API routes.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from loguru import logger
from pathlib import Path

from backend.api.models.document import (
    DocumentGenerationRequest,
    Form5GenerationRequest,
    DocumentGenerationResponse,
)
from backend.services.document_service import get_document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/plan-form1", response_model=DocumentGenerationResponse)
async def generate_plan_form1(request: DocumentGenerationRequest):
    """Generate Form 1 (サービス等利用計画書 様式1)."""
    try:
        service = get_document_service()
        document_path = service.generate_plan_form1(
            plan_id=request.plan_id,
            user_id=request.user_id,
            assessment_id=request.assessment_id,
            goal_ids=request.goal_ids,
            service_need_ids=request.service_need_ids,
        )

        return DocumentGenerationResponse(
            plan_id=request.plan_id,
            document_path=document_path,
            document_type="form1",
            message="Form 1 generated successfully",
        )
    except Exception as e:
        logger.error(f"Error generating Form 1: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plan-form5", response_model=DocumentGenerationResponse)
async def generate_plan_form5(request: Form5GenerationRequest):
    """Generate Form 5 (週間計画表 様式5)."""
    try:
        service = get_document_service()
        document_path = service.generate_plan_form5(
            plan_id=request.plan_id,
            user_id=request.user_id,
            service_need_ids=request.service_need_ids,
        )

        return DocumentGenerationResponse(
            plan_id=request.plan_id,
            document_path=document_path,
            document_type="form5",
            message="Form 5 generated successfully",
        )
    except Exception as e:
        logger.error(f"Error generating Form 5: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_document(filename: str):
    """Download generated document."""
    try:
        service = get_document_service()
        file_path = service.output_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
