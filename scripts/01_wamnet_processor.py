#!/usr/bin/env python3
"""
Process WAM NET CSV data for Kitakyushu facilities.

This script:
1. Reads kitakyushu_all.csv from data/raw/
2. Maps WAM NET columns to our schema
3. Normalizes and validates data
4. Outputs JSON for Neo4j import
"""
import sys
import csv
import json
import re
import uuid
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.logger import get_logger

logger = get_logger(__name__)


# District mapping (from address)
DISTRICT_MAP = {
    "門司区": "門司区",
    "若松区": "若松区",
    "戸畑区": "戸畑区",
    "小倉北区": "小倉北区",
    "小倉南区": "小倉南区",
    "八幡東区": "八幡東区",
    "八幡西区": "八幡西区",
}

# Service category mapping
SERVICE_CATEGORY_MAP = {
    "療養介護": "介護給付",
    "生活介護": "介護給付",
    "短期入所": "介護給付",
    "重度障害者等包括支援": "介護給付",
    "施設入所支援": "介護給付",
    "共同生活援助": "訓練等給付",
    "自立訓練（機能訓練）": "訓練等給付",
    "自立訓練（生活訓練）": "訓練等給付",
    "就労移行支援": "訓練等給付",
    "就労継続支援A型": "訓練等給付",
    "就労継続支援B型": "訓練等給付",
    "就労定着支援": "訓練等給付",
    "自立生活援助": "訓練等給付",
    "居宅介護": "介護給付",
    "重度訪問介護": "介護給付",
    "同行援護": "介護給付",
    "行動援護": "介護給付",
}


class WAMNETProcessor:
    """Process WAM NET CSV data."""

    def __init__(self):
        """Initialize processor."""
        self.stats = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "duplicates": 0,
        }
        self.seen_ids = set()

    def extract_district(self, address: str) -> str:
        """Extract district from address."""
        for district in DISTRICT_MAP:
            if district in address:
                return DISTRICT_MAP[district]
        return "不明"

    def normalize_phone(self, phone: str) -> str:
        """Normalize phone number."""
        if not phone:
            return ""
        # Remove hyphens and spaces
        phone = re.sub(r"[-\s()]", "", phone)
        return phone

    def get_service_category(self, service_type: str) -> str:
        """Get service category from service type."""
        return SERVICE_CATEGORY_MAP.get(service_type, "その他")

    def process_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Process a single CSV row."""
        self.stats["total"] += 1

        try:
            # Extract required fields
            facility_number = row.get("事業所番号", "").strip()
            name = row.get("事業所の名称", "").strip()
            corporation_name = row.get("法人の名称", "").strip()
            service_type = row.get("サービス種別", "").strip()

            # Validate required fields
            if not all([facility_number, name, service_type]):
                logger.warning(f"Missing required fields for: {name or 'Unknown'}")
                self.stats["invalid"] += 1
                return None

            # Check for duplicates
            if facility_number in self.seen_ids:
                logger.debug(f"Duplicate facility_number: {facility_number}")
                self.stats["duplicates"] += 1
                return None

            self.seen_ids.add(facility_number)

            # Build address
            municipality = row.get("事業所住所（市区町村）", "").strip()
            address_detail = row.get("事業所住所（番地以降）", "").strip()
            full_address = f"{municipality}{address_detail}"

            # Extract district
            district = self.extract_district(full_address)

            # Create facility dict
            facility = {
                "facility_id": str(uuid.uuid4()),
                "name": name,
                "corporation_name": corporation_name,
                "facility_number": facility_number,
                "service_type": service_type,
                "service_category": self.get_service_category(service_type),
                "postal_code": "",  # Not in WAM NET CSV
                "address": full_address,
                "district": district,
                "phone": self.normalize_phone(row.get("事業所電話番号", "")),
                "fax": self.normalize_phone(row.get("事業所FAX番号", "")),
                "capacity": row.get("定員", "").strip() or None,
                "availability_status": "不明",  # Not in WAM NET CSV
                "data_source": "WAM_NET",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            # Convert capacity to int if possible
            if facility["capacity"]:
                try:
                    facility["capacity"] = int(facility["capacity"])
                except ValueError:
                    facility["capacity"] = None

            self.stats["valid"] += 1
            return facility

        except Exception as e:
            logger.error(f"Error processing row: {e}")
            self.stats["invalid"] += 1
            return None

    def process_file(self, csv_path: Path) -> List[Dict[str, Any]]:
        """Process CSV file and return list of facilities."""
        logger.info(f"Processing: {csv_path}")

        facilities = []

        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    facility = self.process_row(row)
                    if facility:
                        facilities.append(facility)

        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            return []

        return facilities

    def get_report(self) -> str:
        """Generate processing report."""
        return f"""
Data Processing Report
======================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Statistics:
-----------
Total records processed: {self.stats['total']}
Valid records: {self.stats['valid']}
Invalid records: {self.stats['invalid']}
Duplicates detected: {self.stats['duplicates']}

Success rate: {self.stats['valid'] / max(self.stats['total'], 1) * 100:.2f}%
"""


def main():
    """Main processing function."""
    logger.info("=" * 60)
    logger.info("WAM NET Data Processor")
    logger.info("=" * 60)

    # Paths
    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(exist_ok=True)

    input_file = raw_dir / "kitakyushu_all.csv"

    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        logger.info("Please run extract_kitakyushu.py first")
        return False

    # Process
    processor = WAMNETProcessor()
    facilities = processor.process_file(input_file)

    if not facilities:
        logger.error("No facilities were processed successfully")
        return False

    # Output JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = processed_dir / f"facilities_{timestamp}.json"

    logger.info(f"Writing {len(facilities)} facilities to: {output_file}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(facilities, f, ensure_ascii=False, indent=2)

    logger.success(f"✓ Wrote {len(facilities)} facilities to {output_file.name}")

    # Generate report
    report = processor.get_report()
    report_file = processed_dir / f"processing_report_{timestamp}.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(report)

    logger.info("=" * 60)
    logger.success("Processing complete!")
    logger.info("=" * 60)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
