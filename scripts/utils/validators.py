"""
データ検証ユーティリティ

事業所データの妥当性を検証するための関数群を提供します。
"""

import re
from typing import Any, Dict, List
from pydantic import BaseModel, Field, field_validator, ValidationError


class FacilityValidator(BaseModel):
    """事業所データのバリデーションモデル"""
    
    facility_id: str = Field(..., description="事業所ID")
    name: str = Field(..., min_length=1, description="事業所名")
    corporation_name: str = Field(..., min_length=1, description="法人名")
    facility_number: str = Field(..., pattern=r"^\d{10}$", description="10桁の事業所番号")
    service_type: str = Field(..., min_length=1, description="サービス種別")
    service_category: str = Field(..., description="サービスカテゴリ")
    postal_code: str | None = Field(None, pattern=r"^\d{3}-\d{4}$", description="郵便番号")
    address: str = Field(..., min_length=1, description="住所")
    district: str = Field(..., description="所在区")
    phone: str = Field(..., description="電話番号")
    
    @field_validator('phone')
    def validate_phone(cls, v):
        """電話番号の形式を検証"""
        # 複数の形式に対応: 093-123-4567, 0931234567, 093-1234-5678等
        patterns = [
            r"^0\d{1,4}-\d{1,4}-\d{4}$",  # ハイフン付き
            r"^0\d{9,10}$"  # ハイフンなし
        ]
        if not any(re.match(pattern, v) for pattern in patterns):
            raise ValueError(f"電話番号の形式が正しくありません: {v}")
        return v
    
    @field_validator('service_category')
    def validate_service_category(cls, v):
        """サービスカテゴリの妥当性を検証"""
        valid_categories = ["介護給付", "訓練等給付", "相談支援"]
        if v not in valid_categories:
            raise ValueError(f"無効なサービスカテゴリ: {v}")
        return v
    
    @field_validator('district')
    def validate_district(cls, v):
        """所在区の妥当性を検証"""
        valid_districts = [
            "門司区", "若松区", "戸畑区", "小倉北区",
            "小倉南区", "八幡東区", "八幡西区"
        ]
        if v not in valid_districts:
            raise ValueError(f"無効な区名: {v}")
        return v


def validate_facility_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    事業所データを検証
    
    Args:
        data: 検証対象のデータ辞書
        
    Returns:
        (is_valid, errors): 検証結果とエラーリスト
    """
    try:
        FacilityValidator(**data)
        return True, []
    except ValidationError as e:
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return False, errors


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, List[str]]:
    """
    必須フィールドの存在を検証
    
    Args:
        data: 検証対象のデータ辞書
        required_fields: 必須フィールドのリスト
        
    Returns:
        (is_valid, missing_fields): 検証結果と不足フィールドリスト
    """
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    return len(missing_fields) == 0, missing_fields


def normalize_phone_number(phone: str) -> str:
    """
    電話番号を正規化（ハイフンを統一的に挿入）
    
    Args:
        phone: 電話番号文字列
        
    Returns:
        正規化された電話番号
    """
    # ハイフンを削除
    digits = re.sub(r'\D', '', phone)
    
    # 市外局番の長さに応じて整形
    if len(digits) == 10:
        # 0AB-CDE-FGHI形式 (093-123-4567)
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11:
        # 0ABC-DE-FGHI形式 (0930-12-3456)
        return f"{digits[:4]}-{digits[4:6]}-{digits[6:]}"
    else:
        # そのまま返す
        return phone


def validate_postal_code(postal_code: str) -> bool:
    """
    郵便番号の形式を検証
    
    Args:
        postal_code: 郵便番号文字列
        
    Returns:
        有効な場合True
    """
    pattern = r"^\d{3}-\d{4}$"
    return bool(re.match(pattern, postal_code))


def validate_facility_number(facility_number: str) -> bool:
    """
    事業所番号の形式を検証（10桁の数字）
    
    Args:
        facility_number: 事業所番号文字列
        
    Returns:
        有効な場合True
    """
    pattern = r"^\d{10}$"
    return bool(re.match(pattern, facility_number))


def check_duplicate_facility_id(facility_id: str, existing_ids: List[str]) -> bool:
    """
    事業所IDの重複をチェック
    
    Args:
        facility_id: チェック対象の事業所ID
        existing_ids: 既存の事業所IDリスト
        
    Returns:
        重複している場合True
    """
    return facility_id in existing_ids


def sanitize_text(text: str) -> str:
    """
    テキストをサニタイズ（前後の空白削除、改行の正規化）
    
    Args:
        text: サニタイズ対象のテキスト
        
    Returns:
        サニタイズされたテキスト
    """
    if not text:
        return ""
    
    # 前後の空白を削除
    text = text.strip()
    
    # 連続する空白を1つに
    text = re.sub(r'\s+', ' ', text)
    
    return text


# 使用例
if __name__ == "__main__":
    # テストデータ
    test_data = {
        "facility_id": "test-001",
        "name": "テスト事業所",
        "corporation_name": "社会福祉法人テスト会",
        "facility_number": "4010100123",
        "service_type": "就労継続支援B型",
        "service_category": "訓練等給付",
        "postal_code": "802-0001",
        "address": "福岡県北九州市小倉北区浅野1-1-1",
        "district": "小倉北区",
        "phone": "093-123-4567"
    }
    
    is_valid, errors = validate_facility_data(test_data)
    print(f"検証結果: {is_valid}")
    if not is_valid:
        print(f"エラー: {errors}")
