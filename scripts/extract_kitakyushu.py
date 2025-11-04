#!/usr/bin/env python3
"""
Extract Kitakyushu City data from nationwide WAM NET CSV files.

This script:
1. Reads all CSV files in data/raw/
2. Filters for Kitakyushu city codes
3. Combines into a single CSV
"""
import sys
import csv
from pathlib import Path
from loguru import logger

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Kitakyushu city codes (北九州市の市区町村コード)
KITAKYUSHU_CODES = [
    "40100",  # 北九州市
    "40101",  # 門司区
    "40103",  # 若松区
    "40105",  # 戸畑区
    "40106",  # 小倉北区
    "40107",  # 小倉南区
    "40108",  # 八幡東区
    "40109",  # 八幡西区
]


def extract_kitakyushu_data():
    """Extract Kitakyushu city data from all CSV files."""
    logger.info("=" * 60)
    logger.info("Kitakyushu Data Extraction")
    logger.info("=" * 60)

    # Paths
    raw_dir = project_root / "data" / "raw"
    output_file = raw_dir / "kitakyushu_all.csv"

    # Find all CSV files (excluding sample and previous output)
    csv_files = [
        f
        for f in raw_dir.glob("csvdownload*.csv")
        if f.name != "sample_facilities.csv"
    ]

    if not csv_files:
        logger.error("No CSV files found in data/raw/")
        return False

    logger.info(f"Found {len(csv_files)} CSV files to process")

    all_rows = []
    header = None
    total_processed = 0
    kitakyushu_count = 0

    for csv_file in csv_files:
        logger.info(f"Processing: {csv_file.name}")

        try:
            with open(csv_file, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)

                # Read header from first file
                file_header = next(reader)
                if header is None:
                    header = file_header
                    logger.info(f"Header columns: {len(header)}")

                # Process rows
                for row in reader:
                    total_processed += 1

                    if len(row) < 1:
                        continue

                    # Check if row is from Kitakyushu
                    code = row[0].strip('"')  # Remove quotes if present

                    if code in KITAKYUSHU_CODES:
                        all_rows.append(row)
                        kitakyushu_count += 1

        except Exception as e:
            logger.error(f"Error processing {csv_file.name}: {e}")
            continue

    logger.info(f"\nTotal rows processed: {total_processed}")
    logger.info(f"Kitakyushu rows found: {kitakyushu_count}")

    if kitakyushu_count == 0:
        logger.warning("No Kitakyushu data found!")
        return False

    # Write combined CSV
    logger.info(f"\nWriting to: {output_file}")

    try:
        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(all_rows)

        logger.success(f"✓ Successfully wrote {kitakyushu_count} rows to {output_file.name}")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.error(f"Error writing output file: {e}")
        return False


if __name__ == "__main__":
    success = extract_kitakyushu_data()
    sys.exit(0 if success else 1)
