# -*- coding: utf-8 -*-
"""
Plan API models.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class GoalData(BaseModel):
    """Goal data for plan creation."""

    goal: str = Field(..., description="目標内容")
    period: Optional[str] = Field(None, description="評価期間")
    criteria: Optional[str] = Field(None, description="評価基準")


class ServiceData(BaseModel):
    """Service coordination data."""

    service_type: str = Field(..., description="サービス種別")
    facility_id: Optional[str] = Field(None, description="事業所ID")
    facility_name: Optional[str] = Field(None, description="事業所名")
    frequency: Optional[str] = Field(None, description="利用頻度")
    start_date: Optional[date] = Field(None, description="利用開始予定日")


class PlanBase(BaseModel):
    """Base plan model."""

    plan_type: str = Field("個別支援計画", description="計画種別")
    status: str = Field("draft", description="計画ステータス（draft/active/completed）")


class PlanCreate(BaseModel):
    """Plan creation request."""

    user_id: str = Field(..., description="利用者ID")
    assessment_id: str = Field(..., description="アセスメントID")
    long_term_goals: List[GoalData] = Field(default_factory=list, description="長期目標リスト")
    short_term_goals: List[GoalData] = Field(default_factory=list, description="短期目標リスト")
    services: List[ServiceData] = Field(default_factory=list, description="サービス調整リスト")
    plan_type: str = Field("個別支援計画", description="計画種別")
    status: str = Field("draft", description="計画ステータス")


class PlanUpdate(BaseModel):
    """Plan update request."""

    status: Optional[str] = None
    plan_type: Optional[str] = None


class GoalResponse(BaseModel):
    """Goal response model."""

    goal_id: str
    plan_id: str
    goal_type: str
    goal_text: str
    evaluation_period: Optional[str] = None
    evaluation_criteria: Optional[str] = None
    goal_order: int
    created_at: datetime
    updated_at: datetime


class Plan(PlanBase):
    """Plan response model."""

    plan_id: str
    user_id: str
    assessment_id: str
    long_term_goals: List[GoalResponse] = Field(default_factory=list)
    short_term_goals: List[GoalResponse] = Field(default_factory=list)
    services: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlanListResponse(BaseModel):
    """Plan list response."""

    plans: List[Plan]
    total: int
    page: int
    page_size: int
