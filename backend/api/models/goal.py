# -*- coding: utf-8 -*-
"""
Goal API models.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class SMARTEvaluation(BaseModel):
    """SMART criteria evaluation."""

    is_specific: bool = Field(..., description="具体的か")
    is_measurable: bool = Field(..., description="測定可能か")
    is_achievable: bool = Field(..., description="達成可能か")
    is_relevant: bool = Field(..., description="関連性があるか")
    is_time_bound: bool = Field(..., description="期限付きか")


class GoalBase(BaseModel):
    """Base goal model."""

    goal_text: str = Field(..., description="目標内容", min_length=1)
    goal_type: str = Field(..., description="目標種別（長期目標/短期目標）")
    goal_reason: Optional[str] = Field(None, description="目標設定理由")
    evaluation_period: Optional[str] = Field(None, description="評価期間")
    evaluation_method: Optional[str] = Field(None, description="評価方法")


class GoalCreate(GoalBase):
    """Goal creation request."""

    plan_id: str = Field(..., description="計画ID")
    smart_evaluation: Optional[SMARTEvaluation] = Field(
        None, description="SMART評価"
    )
    confidence: Optional[float] = Field(None, description="信頼度", ge=0.0, le=1.0)


class GoalUpdate(BaseModel):
    """Goal update request."""

    goal_text: Optional[str] = Field(None, min_length=1)
    goal_reason: Optional[str] = None
    evaluation_period: Optional[str] = None
    evaluation_method: Optional[str] = None
    smart_evaluation: Optional[SMARTEvaluation] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class Goal(GoalBase):
    """Goal response model."""

    goal_id: str
    plan_id: str
    smart_evaluation: Optional[SMARTEvaluation]
    confidence: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoalSuggestionRequest(BaseModel):
    """Goal suggestion request."""

    assessment_id: str = Field(..., description="アセスメントID")
    goal_type: str = Field("長期目標", description="目標種別（長期目標/短期目標）")


class GoalSuggestion(BaseModel):
    """Single goal suggestion."""

    goal_text: str
    goal_reason: str
    evaluation_period: str
    evaluation_method: str
    smart_evaluation: SMARTEvaluation
    confidence: float


class GoalSuggestionResponse(BaseModel):
    """Goal suggestion response."""

    assessment_id: str
    goal_type: str
    suggestions: List[GoalSuggestion]


class SMARTEvaluationRequest(BaseModel):
    """SMART evaluation request."""

    goal_text: str = Field(..., description="評価する目標", min_length=1)


class SMARTEvaluationResponse(BaseModel):
    """SMART evaluation response."""

    goal_text: str
    is_specific: bool
    is_measurable: bool
    is_achievable: bool
    is_relevant: bool
    is_time_bound: bool
    smart_score: float = Field(..., description="SMART得点（0.0-1.0）")
    suggestions: List[str] = Field([], description="改善提案")
