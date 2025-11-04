# -*- coding: utf-8 -*-
"""
ServiceNeed API models.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ServiceNeedBase(BaseModel):
    """Base service need model."""

    service_type: str = Field(..., description="サービス種別")
    frequency: str = Field(..., description="利用頻度（例: 週3回）")
    priority: str = Field(..., description="優先度（必須/推奨/オプション）")
    reason: str = Field(..., description="サービスが必要な理由")
    duration_hours: Optional[float] = Field(None, description="1回あたりの利用時間")
    preferred_time: Optional[str] = Field(None, description="希望時間帯（午前/午後）")
    special_requirements: Optional[str] = Field(None, description="特別な要件")


class ServiceNeedCreate(ServiceNeedBase):
    """Service need creation request."""

    plan_id: str = Field(..., description="計画ID")
    goal_id: Optional[str] = Field(None, description="関連する目標ID")


class ServiceNeedUpdate(BaseModel):
    """Service need update request."""

    frequency: Optional[str] = None
    priority: Optional[str] = None
    duration_hours: Optional[float] = None
    preferred_time: Optional[str] = None
    special_requirements: Optional[str] = None
    facility_id: Optional[str] = Field(None, description="割り当てられた事業所ID")


class ServiceNeed(ServiceNeedBase):
    """Service need response model."""

    service_need_id: str
    plan_id: str
    goal_id: Optional[str]
    facility_id: Optional[str] = Field(None, description="割り当てられた事業所ID")
    facility_name: Optional[str] = Field(None, description="事業所名")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceSuggestionRequest(BaseModel):
    """Service suggestion request."""

    user_id: str = Field(..., description="利用者ID")
    assessment_id: str = Field(..., description="アセスメントID")
    goal_ids: List[str] = Field(..., description="目標IDリスト")


class ServiceSuggestion(BaseModel):
    """Single service suggestion."""

    service_type: str
    frequency: str
    priority: str
    reason: str
    duration_hours: Optional[float]
    preferred_time: Optional[str]
    special_requirements: Optional[str]


class ServiceSuggestionResponse(BaseModel):
    """Service suggestion response."""

    user_id: str
    suggestions: List[ServiceSuggestion]


class FacilityMatch(BaseModel):
    """Matched facility with score."""

    facility_id: str
    name: str
    corporation_name: str
    address: str
    district: str
    service_type: str
    capacity: Optional[int]
    availability_status: Optional[str]
    match_score: float = Field(..., description="マッチングスコア（0.0-1.0）", ge=0.0, le=1.0)
    match_reasons: List[str] = Field(..., description="推薦理由")
    match_concerns: List[str] = Field([], description="懸念点")


class FacilityMatchRequest(BaseModel):
    """Facility matching request."""

    user_id: str = Field(..., description="利用者ID")
    assessment_id: str = Field(..., description="アセスメントID")
    service_type: str = Field(..., description="サービス種別")
    limit: int = Field(10, description="最大件数", ge=1, le=50)


class FacilityMatchResponse(BaseModel):
    """Facility matching response."""

    service_type: str
    matched_facilities: List[FacilityMatch]
