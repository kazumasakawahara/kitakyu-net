# -*- coding: utf-8 -*-
"""
Document generation API models.
"""
from pydantic import BaseModel, Field
from typing import List


class DocumentGenerationRequest(BaseModel):
    """Document generation request."""

    plan_id: str = Field(..., description="計画ID")
    user_id: str = Field(..., description="利用者ID")
    assessment_id: str = Field(..., description="アセスメントID")
    goal_ids: List[str] = Field(..., description="目標IDリスト")
    service_need_ids: List[str] = Field(..., description="サービスニーズIDリスト")


class Form5GenerationRequest(BaseModel):
    """Form 5 generation request."""

    plan_id: str = Field(..., description="計画ID")
    user_id: str = Field(..., description="利用者ID")
    service_need_ids: List[str] = Field(..., description="サービスニーズIDリスト")


class DocumentGenerationResponse(BaseModel):
    """Document generation response."""

    plan_id: str
    document_path: str = Field(..., description="生成されたドキュメントのパス")
    document_type: str = Field(..., description="ドキュメントタイプ（form1/form5）")
    message: str = Field("Document generated successfully", description="メッセージ")
