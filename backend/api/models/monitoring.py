# -*- coding: utf-8 -*-
"""
Monitoring API models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MonitoringType(str, Enum):
    """モニタリング種別"""
    REGULAR = "定期"
    EMERGENCY = "臨時"
    FINAL = "終結時"


class MonitoringStatus(str, Enum):
    """モニタリングステータス"""
    IN_PROGRESS = "進行中"
    COMPLETED = "完了"
    NEEDS_IMPROVEMENT = "要改善"


class AchievementStatus(str, Enum):
    """達成状況"""
    NOT_ACHIEVED = "未達成"
    PARTIALLY_ACHIEVED = "一部達成"
    ACHIEVED = "達成"
    EXCEEDED = "超過達成"


class GoalEvaluation(BaseModel):
    """目標評価"""
    goal_id: str = Field(..., description="目標ID")
    goal_type: str = Field(..., description="目標種別 (long_term/short_term)")
    achievement_rate: int = Field(..., ge=0, le=100, description="達成率 (0-100%)")
    evaluation_comment: str = Field(..., description="評価コメント")
    achievement_status: AchievementStatus = Field(..., description="達成状況")
    evidence: Optional[str] = Field(None, description="根拠・具体例")
    next_action: Optional[str] = Field(None, description="次のアクション")


class ServiceEvaluation(BaseModel):
    """サービス評価"""
    service_id: str = Field(..., description="サービスID")
    service_name: str = Field(..., description="サービス名")
    attendance_rate: Optional[int] = Field(None, ge=0, le=100, description="出席率 (0-100%)")
    service_satisfaction: Optional[int] = Field(None, ge=1, le=5, description="満足度 (1-5点)")
    effectiveness: Optional[str] = Field(None, description="効果・変化")
    issues: Optional[str] = Field(None, description="課題・問題点")
    adjustment_needed: bool = Field(False, description="調整が必要")


class NewGoalProposal(BaseModel):
    """新目標案"""
    goal_text: str = Field(..., description="目標内容")
    goal_type: str = Field(..., description="目標種別 (long_term/short_term)")
    evaluation_period: Optional[str] = Field(None, description="評価期間")
    evaluation_criteria: Optional[str] = Field(None, description="評価基準")


class ServiceChangeProposal(BaseModel):
    """サービス変更案"""
    change_type: str = Field(..., description="変更種別 (追加/変更/中止)")
    service_id: Optional[str] = Field(None, description="既存サービスID (変更/中止の場合)")
    service_type: Optional[str] = Field(None, description="サービス種別 (追加/変更の場合)")
    facility_name: Optional[str] = Field(None, description="事業所名 (追加/変更の場合)")
    reason: str = Field(..., description="変更理由")


class MonitoringBase(BaseModel):
    """モニタリング記録基本モデル"""
    plan_id: str = Field(..., description="計画ID")
    monitoring_date: datetime = Field(..., description="記録日")
    monitoring_type: MonitoringType = Field(..., description="モニタリング種別")
    status: MonitoringStatus = Field(..., description="ステータス")

    # 目標評価
    goal_evaluations: List[GoalEvaluation] = Field(default_factory=list, description="目標評価リスト")

    # サービス評価
    service_evaluations: List[ServiceEvaluation] = Field(default_factory=list, description="サービス評価リスト")

    # 総合評価
    overall_summary: str = Field(..., description="総合評価サマリー")
    strengths: List[str] = Field(default_factory=list, description="良かった点")
    challenges: List[str] = Field(default_factory=list, description="課題")
    family_feedback: Optional[str] = Field(None, description="家族の意見")

    # 計画変更
    plan_revision_needed: bool = Field(False, description="計画変更が必要")
    revision_reason: Optional[str] = Field(None, description="変更理由")
    new_goals: List[NewGoalProposal] = Field(default_factory=list, description="新目標案")
    service_changes: List[ServiceChangeProposal] = Field(default_factory=list, description="サービス変更案")


class MonitoringCreate(MonitoringBase):
    """モニタリング記録作成モデル"""
    created_by: str = Field(..., description="作成者ID")


class MonitoringUpdate(BaseModel):
    """モニタリング記録更新モデル"""
    monitoring_date: Optional[datetime] = None
    monitoring_type: Optional[MonitoringType] = None
    status: Optional[MonitoringStatus] = None
    goal_evaluations: Optional[List[GoalEvaluation]] = None
    service_evaluations: Optional[List[ServiceEvaluation]] = None
    overall_summary: Optional[str] = None
    strengths: Optional[List[str]] = None
    challenges: Optional[List[str]] = None
    family_feedback: Optional[str] = None
    plan_revision_needed: Optional[bool] = None
    revision_reason: Optional[str] = None
    new_goals: Optional[List[NewGoalProposal]] = None
    service_changes: Optional[List[ServiceChangeProposal]] = None


class MonitoringRecord(MonitoringBase):
    """モニタリング記録モデル（レスポンス）"""
    monitoring_id: str = Field(..., description="モニタリング記録ID")
    created_by: str = Field(..., description="作成者ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        json_schema_extra = {
            "example": {
                "monitoring_id": "mon_12345",
                "plan_id": "plan_67890",
                "monitoring_date": "2024-12-01T10:00:00",
                "monitoring_type": "定期",
                "status": "進行中",
                "goal_evaluations": [
                    {
                        "goal_id": "goal_1",
                        "goal_type": "long_term",
                        "achievement_rate": 75,
                        "evaluation_comment": "順調に進んでいます",
                        "achievement_status": "一部達成",
                        "evidence": "週2回の通所を継続できている",
                        "next_action": "作業内容のステップアップを検討"
                    }
                ],
                "service_evaluations": [
                    {
                        "service_id": "service_1",
                        "service_name": "就労継続支援B型",
                        "attendance_rate": 90,
                        "service_satisfaction": 4,
                        "effectiveness": "作業意欲が向上している",
                        "issues": "特になし",
                        "adjustment_needed": False
                    }
                ],
                "overall_summary": "全体的に順調に進捗しています",
                "strengths": ["通所の習慣が定着", "作業意欲の向上"],
                "challenges": ["作業の正確性向上"],
                "family_feedback": "本人が楽しそうに通っている",
                "plan_revision_needed": False,
                "revision_reason": None,
                "new_goals": [],
                "service_changes": [],
                "created_by": "staff_123",
                "created_at": "2024-12-01T10:00:00",
                "updated_at": "2024-12-01T10:00:00"
            }
        }


class ProgressTimeline(BaseModel):
    """進捗タイムラインデータ"""
    goal_id: str = Field(..., description="目標ID")
    goal_text: str = Field(..., description="目標内容")
    goal_type: str = Field(..., description="目標種別")
    timeline: List[dict] = Field(..., description="時系列データ [{date, achievement_rate, comment}]")
