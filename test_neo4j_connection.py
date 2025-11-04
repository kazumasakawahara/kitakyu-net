"""
Neo4j connection test script
"""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from backend.neo4j.client import get_neo4j_client
from loguru import logger

def main():
    """Test Neo4j connection and initialize schema."""
    logger.info("=" * 60)
    logger.info("Neo4j Connection Test")
    logger.info("=" * 60)

    # Get Neo4j client
    logger.info("Initializing Neo4j client...")
    neo4j_client = get_neo4j_client()

    # Test connection
    logger.info("Testing Neo4j connection...")
    if neo4j_client.verify_connection():
        logger.success("✓ Neo4j connection successful")
    else:
        logger.error("✗ Neo4j connection failed")
        return False
    
    # Initialize schema
    logger.info("Initializing database schema...")
    try:
        neo4j_client.initialize_schema()
        logger.success("✓ Schema initialization successful")
    except Exception as e:
        logger.error(f"✗ Schema initialization failed: {e}")
        return False
    
    # Get statistics
    logger.info("Fetching database statistics...")
    try:
        stats = neo4j_client.get_statistics()
        logger.info(f"Total facilities: {stats['total_facilities']}")
        logger.info(f"By service type: {stats['by_service_type']}")
        logger.info(f"By district: {stats['by_district']}")
        logger.success("✓ Statistics retrieved successfully")
    except Exception as e:
        logger.error(f"✗ Failed to get statistics: {e}")
        return False
    
    logger.info("=" * 60)
    logger.success("All tests passed!")
    logger.info("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
