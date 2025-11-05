# -*- coding: utf-8 -*-
"""
User data models for API.
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base user model with common fields."""

    name: str = Field(..., description="氏名", min_length=1)
    kana: Optional[str] = Field(None, description="フリガナ")
    birth_date: date = Field(..., description="生年月日")
    gender: Optional[str] = Field(None, description="性別")
    disability_type: str = Field(..., description="障害種別")
    disability_grade: Optional[str] = Field(None, description="障害等級")
    support_level: Optional[str] = Field(None, description="障害支援区分")
    therapy_notebook: Optional[bool] = Field(None, description="療育手帳の有無")
    therapy_notebook_grade: Optional[str] = Field(None, description="療育手帳等級 (A/B1/B2/A3)")
    mental_health_notebook: Optional[bool] = Field(None, description="精神保健福祉手帳の有無")
    mental_health_notebook_grade: Optional[str] = Field(None, description="精神保健福祉手帳等級 (1級/2級/3級)")
    mental_health_notebook_expiry: Optional[date] = Field(None, description="精神保健福祉手帳有効期限")
    medical_care_needs: Optional[bool] = Field(None, description="医療的ケア")
    behavioral_support_needs: Optional[bool] = Field(
        None, description="強度行動障害"
    )
    living_situation: Optional[str] = Field(None, description="居住状況")
    family_structure: Optional[str] = Field(None, description="家族構成")
    guardian_name: Optional[str] = Field(None, description="保護者名")
    guardian_relation: Optional[str] = Field(None, description="続柄")
    contact_phone: Optional[str] = Field(None, description="連絡先電話番号")
    contact_address: Optional[str] = Field(None, description="住所")


class UserCreate(UserBase):
    """Model for creating new user."""

    pass


class UserUpdate(BaseModel):
    """Model for updating existing user (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1)
    kana: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    disability_type: Optional[str] = None
    disability_grade: Optional[str] = None
    support_level: Optional[str] = None
    therapy_notebook: Optional[bool] = None
    therapy_notebook_grade: Optional[str] = None
    mental_health_notebook: Optional[bool] = None
    mental_health_notebook_grade: Optional[str] = None
    mental_health_notebook_expiry: Optional[date] = None
    medical_care_needs: Optional[bool] = None
    behavioral_support_needs: Optional[bool] = None
    living_situation: Optional[str] = None
    family_structure: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_relation: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None


class User(UserBase):
    """Complete user model with system fields."""

    user_id: str = Field(..., description="ユーザーID (UUID)")
    age: Optional[int] = Field(None, description="年齢（自動計算）")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "山田太郎",
                "kana": "ヤマダタロウ",
                "birth_date": "1980-05-15",
                "age": 45,
                "gender": "男性",
                "disability_type": "知的障害",
                "disability_grade": "重度",
                "support_level": "区分4",
                "therapy_notebook": True,
                "therapy_notebook_grade": "A",
                "mental_health_notebook": False,
                "mental_health_notebook_grade": None,
                "mental_health_notebook_expiry": None,
                "medical_care_needs": False,
                "behavioral_support_needs": False,
                "living_situation": "在宅",
                "family_structure": "本人、母",
                "guardian_name": "山田花子",
                "guardian_relation": "母",
                "contact_phone": "090-1234-5678",
                "contact_address": "北九州市小倉北区...",
                "created_at": "2025-10-31T10:00:00",
                "updated_at": "2025-10-31T10:00:00",
            }
        }


class UserList(BaseModel):
    """Model for user list response."""

    users: List[User]
    total: int = Field(..., description="総件数")
    page: int = Field(1, description="現在のページ")
    page_size: int = Field(20, description="ページサイズ")


class UserFilter(BaseModel):
    """Model for user filtering."""

    disability_type: Optional[str] = None
    support_level: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    living_situation: Optional[str] = None
    search_query: Optional[str] = Field(None, description="名前・カナで検索")


class UserDeleteResponse(BaseModel):
    """Response for user deletion."""

    status: str = Field("deleted", description="削除状態")
    user_id: str = Field(..., description="削除されたユーザーID")
    message: str = Field(..., description="メッセージ")
