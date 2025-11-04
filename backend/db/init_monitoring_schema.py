# -*- coding: utf-8 -*-
"""
Initialize monitoring schema in Neo4j.
"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def init_monitoring_schema():
    """Initialize monitoring schema with constraints and indexes."""

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        with driver.session() as session:
            # Create unique constraint for monitoring_id
            logger.info("Creating unique constraint for monitoring_id...")
            session.run("""
                CREATE CONSTRAINT monitoring_id_unique IF NOT EXISTS
                FOR (m:MonitoringRecord) REQUIRE m.monitoring_id IS UNIQUE
            """)

            # Create index on monitoring_date
            logger.info("Creating index on monitoring_date...")
            session.run("""
                CREATE INDEX monitoring_date_index IF NOT EXISTS
                FOR (m:MonitoringRecord) ON (m.monitoring_date)
            """)

            # Create index on status
            logger.info("Creating index on status...")
            session.run("""
                CREATE INDEX monitoring_status_index IF NOT EXISTS
                FOR (m:MonitoringRecord) ON (m.status)
            """)

            # Create index on monitoring_type
            logger.info("Creating index on monitoring_type...")
            session.run("""
                CREATE INDEX monitoring_type_index IF NOT EXISTS
                FOR (m:MonitoringRecord) ON (m.monitoring_type)
            """)

            logger.info("Monitoring schema initialized successfully!")

    except Exception as e:
        logger.error(f"Error initializing monitoring schema: {e}")
        raise
    finally:
        driver.close()


if __name__ == "__main__":
    init_monitoring_schema()
