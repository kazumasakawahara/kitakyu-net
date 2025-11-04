# -*- coding: utf-8 -*-
"""
Assessment data models for API.
"""
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field


class ICFClassification(BaseModel):
    """ICF model classification."""

    body_functions: str = Field("", description="心身機能")
    activities: str = Field("", description="活動")
    participation: str = Field("", description="参加")
    environmental_factors: str = Field("", description="環境因子")
    personal_factors: str = Field("", description="個人因子")


class AssessmentAnalysis(BaseModel):
    """LLM analysis results."""

    analyzed_needs: List[str] = Field([], description="分析されたニーズ")
    strengths: List[str] = Field([], description="強み")
    challenges: List[str] = Field([], description="課題")
    preferences: List[str] = Field([], description="本人の希望")
    family_wishes: List[str] = Field([], description="家族の希望")
    icf_classification: ICFClassification = Field(..., description="ICF分類")
    confidence_score: Optional[float] = Field(None, description="信頼度スコア")


class AssessmentCreate(BaseModel):
    """Model for creating new assessment."""

    user_id: str = Field(..., description="利用者ID")
    interview_date: date = Field(..., description="面談日")
    interview_participants: Optional[str] = Field(None, description="ヒアリング参加者")
    interview_content: str = Field(..., description="ヒアリング内容", min_length=10)
    analyze: bool = Field(False, description="LLM分析を実行するか")


class AssessmentUpdate(BaseModel):
    """Model for updating assessment."""

    interview_date: Optional[date] = None
    interview_participants: Optional[str] = None
    interview_content: Optional[str] = Field(None, min_length=10)
    analyzed_needs: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    challenges: Optional[List[str]] = None
    preferences: Optional[List[str]] = None
    family_wishes: Optional[List[str]] = None


class Assessment(BaseModel):
    """Complete assessment model."""

    assessment_id: str = Field(..., description="アセスメントID")
    user_id: str = Field(..., description="利用者ID")
    interview_date: date = Field(..., description="面談日")
    interview_participants: Optional[str] = Field(None, description="ヒアリング参加者")
    interview_content: str = Field(..., description="ヒアリング内容")

    # LLM analysis results
    analyzed_needs: Optional[List[str]] = Field(None, description="分析されたニーズ")
    strengths: Optional[List[str]] = Field(None, description="強み")
    challenges: Optional[List[str]] = Field(None, description="課題")
    preferences: Optional[List[str]] = Field(None, description="本人の希望")
    family_wishes: Optional[List[str]] = Field(None, description="家族の希望")

    # ICF classification
    body_functions: Optional[str] = Field(None, description="心身機能")
    activities: Optional[str] = Field(None, description="活動")
    participation: Optional[str] = Field(None, description="参加")
    environmental_factors: Optional[str] = Field(None, description="環境因子")
    personal_factors: Optional[str] = Field(None, description="個人因子")

    confidence_score: Optional[float] = Field(None, description="分析信頼度")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")


class AssessmentWithAnalysis(Assessment):
    """Assessment with analysis object."""

    analysis: Optional[AssessmentAnalysis] = Field(None, description="分析結果")


class AnalyzeRequest(BaseModel):
    """Request to analyze assessment."""

    timeout: int = Field(60, description="タイムアウト（秒）", ge=10, le=120)


class AnalyzeResponse(BaseModel):
    """Response from analysis."""

    assessment_id: str
    analysis: AssessmentAnalysis
    message: str
