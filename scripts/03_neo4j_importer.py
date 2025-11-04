#!/usr/bin/env python3
"""
Neo4j importer for processed facility data.

This script:
1. Reads processed JSON data
2. Imports facilities into Neo4j database
3. Uses MERGE to avoid duplicates
4. Provides import statistics
"""
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.logger import get_logger
from backend.neo4j.client import get_neo4j_client

logger = get_logger(__name__)


class Neo4jFacilityImporter:
    """Import facility data into Neo4j."""

    def __init__(self):
        """Initialize importer."""
        self.client = get_neo4j_client()
        self.stats = {
            "total": 0,
            "created": 0,
            "updated": 0,
            "errors": 0,
        }

    def import_facility(self, facility: Dict[str, Any]) -> bool:
        """Import a single facility into Neo4j."""
        self.stats["total"] += 1

        query = """
        MERGE (f:Facility {facility_id: $facility_id})
        ON CREATE SET
            f.name = $name,
            f.corporation_name = $corporation_name,
            f.facility_number = $facility_number,
            f.service_type = $service_type,
            f.service_category = $service_category,
            f.postal_code = $postal_code,
            f.address = $address,
            f.district = $district,
            f.phone = $phone,
            f.fax = $fax,
            f.capacity = $capacity,
            f.availability_status = $availability_status,
            f.data_source = $data_source,
            f.created_at = datetime($created_at),
            f.updated_at = datetime($updated_at)
        ON MATCH SET
            f.name = $name,
            f.corporation_name = $corporation_name,
            f.service_type = $service_type,
            f.service_category = $service_category,
            f.postal_code = $postal_code,
            f.address = $address,
            f.district = $district,
            f.phone = $phone,
            f.fax = $fax,
            f.capacity = $capacity,
            f.availability_status = $availability_status,
            f.updated_at = datetime($updated_at)
        RETURN f, 
               CASE WHEN f.created_at = datetime($created_at) THEN 'created' ELSE 'updated' END as action
        """

        try:
            result = self.client.execute_query(query, facility)
            if result:
                action = result[0].get("action", "unknown")
                if action == "created":
                    self.stats["created"] += 1
                else:
                    self.stats["updated"] += 1
                return True
            else:
                self.stats["errors"] += 1
                return False
        except Exception as e:
            logger.error(f"Failed to import facility {facility.get('name')}: {e}")
            self.stats["errors"] += 1
            return False

    def import_batch(self, facilities: List[Dict[str, Any]], batch_size: int = 100):
        """Import facilities in batches."""
        total = len(facilities)
        logger.info(f"Importing {total} facilities in batches of {batch_size}...")

        for i in range(0, total, batch_size):
            batch = facilities[i : i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1} ({i + 1}-{min(i + batch_size, total)} of {total})")

            for facility in batch:
                self.import_facility(facility)

        logger.info("Import complete")

    def get_import_summary(self) -> str:
        """Generate import summary report."""
        return f"""
Import Summary
==============
Total facilities: {self.stats['total']}
Created: {self.stats['created']}
Updated: {self.stats['updated']}
Errors: {self.stats['errors']}

Success rate: {(self.stats['created'] + self.stats['updated']) / max(self.stats['total'], 1) * 100:.2f}%
"""


def main():
    """Main import function."""
    logger.info("=" * 60)
    logger.info("Neo4j Facility Importer")
    logger.info("=" * 60)

    # Paths
    processed_dir = Path(__file__).parent.parent / "data" / "processed"

    # Find latest processed JSON
    json_files = list(processed_dir.glob("facilities_*.json"))

    if not json_files:
        logger.error(f"No processed JSON files found in {processed_dir}")
        logger.info("Please run 02_data_processor.py first")
        return False

    # Use the latest file
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Using file: {latest_file}")

    # Load data
    with open(latest_file, "r", encoding="utf-8") as f:
        facilities = json.load(f)

    logger.info(f"Loaded {len(facilities)} facilities")

    # Import
    importer = Neo4jFacilityImporter()
    importer.import_batch(facilities)

    # Print summary
    summary = importer.get_import_summary()
    logger.info(summary)
    print(summary)

    # Verify import
    logger.info("Verifying import...")
    client = get_neo4j_client()
    count = client.get_facility_count()
    logger.info(f"Total facilities in database: {count}")

    logger.info("=" * 60)
    logger.success("Import complete!")
    logger.info("=" * 60)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
