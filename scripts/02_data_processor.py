#!/usr/bin/env python3
"""
Data processor for WAM NET facility data.

This script:
1. Reads raw CSV data from WAM NET
2. Validates and normalizes facility data
3. Generates UUIDs for facilities
4. Outputs processed JSON for Neo4j import
"""
import sys
import uuid
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.logger import get_logger

logger = get_logger(__name__)


class FacilityDataProcessor:
    """Process and validate facility data from WAM NET."""

    # Service type mapping
    SERVICE_TYPE_MAPPING = {
        "生活介護": "生活介護",
        "就労継続支援A型": "就労継続支援A型",
        "就労継続支援B型": "就労継続支援B型",
        "就労移行支援": "就労移行支援",
        "就労定着支援": "就労定着支援",
        "自立訓練（機能訓練）": "自立訓練（機能訓練）",
        "自立訓練（生活訓練）": "自立訓練（生活訓練）",
        "共同生活援助": "共同生活援助",
        "短期入所": "短期入所",
        "療養介護": "療養介護",
        "施設入所支援": "施設入所支援",
        "相談支援": "相談支援",
    }

    # Service category mapping
    SERVICE_CATEGORY_MAPPING = {
        "生活介護": "介護給付",
        "療養介護": "介護給付",
        "短期入所": "介護給付",
        "施設入所支援": "介護給付",
        "共同生活援助": "介護給付",
        "就労継続支援A型": "訓練等給付",
        "就労継続支援B型": "訓練等給付",
        "就労移行支援": "訓練等給付",
        "就労定着支援": "訓練等給付",
        "自立訓練（機能訓練）": "訓練等給付",
        "自立訓練（生活訓練）": "訓練等給付",
        "相談支援": "相談支援",
    }

    # District mapping for Kitakyushu
    DISTRICTS = [
        "小倉北区",
        "小倉南区",
        "八幡東区",
        "八幡西区",
        "戸畑区",
        "門司区",
        "若松区",
    ]

    def __init__(self):
        """Initialize data processor."""
        self.facility_id_map: Dict[str, str] = {}  # facility_number -> facility_id
        self.stats = {
            "total_records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "duplicates": 0,
            "normalization_changes": 0,
        }

    def normalize_postal_code(self, postal_code: str) -> Optional[str]:
        """Normalize postal code to XXX-XXXX format."""
        if pd.isna(postal_code):
            return None

        # Remove all non-digits
        digits = re.sub(r"\D", "", str(postal_code))

        if len(digits) == 7:
            return f"{digits[:3]}-{digits[3:]}"
        else:
            logger.warning(f"Invalid postal code format: {postal_code}")
            return postal_code

    def normalize_phone_number(self, phone: str) -> Optional[str]:
        """Normalize phone number format."""
        if pd.isna(phone):
            return None

        # Remove all non-digits
        digits = re.sub(r"\D", "", str(phone))

        # Common patterns for Kitakyushu area (093)
        if len(digits) == 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11:
            return f"{digits[:4]}-{digits[4:7]}-{digits[7:]}"
        else:
            return phone

    def extract_district(self, address: str) -> Optional[str]:
        """Extract district (区) from address."""
        if pd.isna(address):
            return None

        for district in self.DISTRICTS:
            if district in address:
                return district

        logger.warning(f"Could not extract district from address: {address}")
        return None

    def normalize_service_type(self, service_type: str) -> Optional[str]:
        """Normalize service type name."""
        if pd.isna(service_type):
            return None

        # Direct mapping
        if service_type in self.SERVICE_TYPE_MAPPING:
            return self.SERVICE_TYPE_MAPPING[service_type]

        # Fuzzy matching (contains)
        for key, value in self.SERVICE_TYPE_MAPPING.items():
            if key in service_type:
                return value

        logger.warning(f"Unknown service type: {service_type}")
        return service_type

    def get_service_category(self, service_type: str) -> Optional[str]:
        """Get service category from service type."""
        return self.SERVICE_CATEGORY_MAPPING.get(service_type)

    def generate_facility_id(self, facility_number: str) -> str:
        """Generate or retrieve UUID for facility."""
        if facility_number in self.facility_id_map:
            return self.facility_id_map[facility_number]

        facility_id = str(uuid.uuid4())
        self.facility_id_map[facility_number] = facility_id
        return facility_id

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a single facility record."""
        required_fields = [
            "name",
            "corporation_name",
            "facility_number",
            "service_type",
            "address",
            "phone",
        ]

        for field in required_fields:
            if not record.get(field) or pd.isna(record.get(field)):
                logger.warning(f"Missing required field '{field}' in record: {record.get('name', 'Unknown')}")
                return False

        # Validate facility_number format (10 digits)
        facility_number = str(record["facility_number"])
        if not re.match(r"^\d{10}$", facility_number):
            logger.warning(f"Invalid facility_number format: {facility_number}")
            return False

        return True

    def process_record(self, row: pd.Series) -> Optional[Dict[str, Any]]:
        """Process a single CSV row into facility record."""
        self.stats["total_records"] += 1

        # Basic mapping (adjust based on actual WAM NET CSV columns)
        record = {
            "name": row.get("事業所名"),
            "corporation_name": row.get("法人名"),
            "facility_number": str(row.get("事業所番号", "")).strip(),
            "service_type": row.get("サービス種類"),
            "address": row.get("所在地"),
            "postal_code": row.get("郵便番号"),
            "phone": row.get("電話番号"),
            "fax": row.get("FAX番号"),
            "capacity": row.get("定員"),
        }

        # Validate
        if not self.validate_record(record):
            self.stats["invalid_records"] += 1
            return None

        # Normalize
        record["postal_code"] = self.normalize_postal_code(record["postal_code"])
        record["phone"] = self.normalize_phone_number(record["phone"])
        record["fax"] = self.normalize_phone_number(record["fax"])
        record["district"] = self.extract_district(record["address"])
        record["service_type"] = self.normalize_service_type(record["service_type"])
        record["service_category"] = self.get_service_category(record["service_type"])

        # Generate UUID
        record["facility_id"] = self.generate_facility_id(record["facility_number"])

        # Add metadata
        record["data_source"] = "WAM_NET"
        record["availability_status"] = "不明"
        record["created_at"] = datetime.now().isoformat()
        record["updated_at"] = datetime.now().isoformat()

        # Handle capacity
        if pd.notna(record.get("capacity")):
            try:
                record["capacity"] = int(record["capacity"])
            except (ValueError, TypeError):
                record["capacity"] = None

        self.stats["valid_records"] += 1
        return record

    def process_csv(self, csv_path: Path) -> List[Dict[str, Any]]:
        """Process CSV file and return list of facility records."""
        logger.info(f"Processing CSV file: {csv_path}")

        try:
            df = pd.read_csv(csv_path, encoding="utf-8")
        except UnicodeDecodeError:
            # Try Shift-JIS encoding (common for Japanese CSV)
            df = pd.read_csv(csv_path, encoding="shift-jis")

        logger.info(f"Read {len(df)} rows from CSV")

        facilities = []
        for _, row in df.iterrows():
            facility = self.process_record(row)
            if facility:
                facilities.append(facility)

        return facilities

    def save_processed_data(self, facilities: List[Dict[str, Any]], output_path: Path):
        """Save processed data to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(facilities, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(facilities)} facilities to {output_path}")

    def generate_report(self, output_path: Path):
        """Generate processing report."""
        report = f"""
Data Processing Report
======================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Statistics:
-----------
Total records processed: {self.stats['total_records']}
Valid records: {self.stats['valid_records']}
Invalid records: {self.stats['invalid_records']}
Duplicates detected: {self.stats['duplicates']}
Normalization changes: {self.stats['normalization_changes']}

Success rate: {self.stats['valid_records'] / max(self.stats['total_records'], 1) * 100:.2f}%
"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Report saved to {output_path}")
        print(report)


def main():
    """Main processing function."""
    logger.info("=" * 60)
    logger.info("WAM NET Data Processor")
    logger.info("=" * 60)

    # Paths
    data_dir = Path(__file__).parent.parent / "data"
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"

    # Check for CSV files
    csv_files = list(raw_dir.glob("*.csv"))

    if not csv_files:
        logger.error(f"No CSV files found in {raw_dir}")
        logger.info("Please download WAM NET data and place CSV files in data/raw/")
        return False

    logger.info(f"Found {len(csv_files)} CSV file(s)")

    # Process all CSV files
    processor = FacilityDataProcessor()
    all_facilities = []

    for csv_file in csv_files:
        facilities = processor.process_csv(csv_file)
        all_facilities.extend(facilities)

    # Save processed data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = processed_dir / f"facilities_{timestamp}.json"
    processor.save_processed_data(all_facilities, output_file)

    # Generate report
    report_file = processed_dir / f"processing_report_{timestamp}.txt"
    processor.generate_report(report_file)

    logger.info("=" * 60)
    logger.success("Processing complete!")
    logger.info(f"Processed data: {output_file}")
    logger.info(f"Report: {report_file}")
    logger.info("=" * 60)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
