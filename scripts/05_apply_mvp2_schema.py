#!/usr/bin/env python3
"""
Apply Neo4j schema extensions for MVP2.

This script adds User, Plan, Assessment, Goal, ServiceNeed nodes.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.neo4j.client import get_neo4j_client
from backend.neo4j.schema_extensions import apply_schema_extensions, verify_schema
from scripts.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Apply Neo4j schema extensions."""
    logger.info("=" * 60)
    logger.info("MVP2 Schema Extension")
    logger.info("=" * 60)

    # Get Neo4j client
    neo4j_client = get_neo4j_client()

    # Verify connection
    try:
        neo4j_client._connect()
        logger.success("✓ Connected to Neo4j")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        return False

    # Apply schema extensions
    try:
        count = apply_schema_extensions(neo4j_client)
        logger.info(f"Applied {count} schema elements")
    except Exception as e:
        logger.error(f"Failed to apply schema: {e}")
        return False

    # Verify schema
    try:
        result = verify_schema(neo4j_client)
        if result["valid"]:
            logger.success("✓ Schema verification passed")
            logger.info(f"Node labels: {', '.join(result['labels']['existing'])}")
            logger.info(
                f"Constraints: {len(result['constraints']['existing'])} total"
            )
        else:
            logger.warning("Schema verification incomplete")
            if result["labels"]["missing"]:
                logger.warning(f"Missing labels: {result['labels']['missing']}")
            if result["constraints"]["missing"]:
                logger.warning(
                    f"Missing constraints: {result['constraints']['missing']}"
                )
    except Exception as e:
        logger.error(f"Failed to verify schema: {e}")
        return False

    logger.info("=" * 60)
    logger.success("MVP2 schema extension complete!")
    logger.info("=" * 60)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
