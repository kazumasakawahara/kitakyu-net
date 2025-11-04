#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct Neo4j test to verify transaction management.
"""
import uuid
from datetime import datetime
from backend.neo4j.client import get_neo4j_client

def test_direct_create():
    """Test direct create operation with execute_write."""
    db = get_neo4j_client()

    # Create test assessment
    assessment_id = str(uuid.uuid4())
    user_id = "2db3f29f-af9b-4022-b314-f2b80f2c637b"  # 正常太郎
    now = datetime.now()

    query = """
    MATCH (u:User {user_id: $user_id})
    CREATE (a:Assessment {
        assessment_id: $assessment_id,
        user_id: $user_id,
        interview_date: date($interview_date),
        interview_content: $interview_content,
        analyzed_needs: $analyzed_needs,
        created_at: datetime($created_at),
        updated_at: datetime($updated_at)
    })
    CREATE (u)-[:HAS_ASSESSMENT]->(a)
    RETURN a
    """

    params = {
        "assessment_id": assessment_id,
        "user_id": user_id,
        "interview_date": "2025-03-15",
        "interview_content": "Direct test content",
        "analyzed_needs": [],
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    print(f"Creating assessment with execute_write: {assessment_id}")
    result = db.execute_write(query, params)

    if result:
        print(f"✅ Assessment created successfully: {result}")
    else:
        print(f"❌ No result returned from execute_write")

    # Verify it exists
    verify_query = """
    MATCH (a:Assessment {assessment_id: $assessment_id})
    RETURN a
    """

    print(f"\nVerifying assessment exists...")
    verify_result = db.execute_read(verify_query, {"assessment_id": assessment_id})

    if verify_result:
        print(f"✅ Assessment found in database: {verify_result}")
    else:
        print(f"❌ Assessment NOT found in database")

    # Count all assessments
    count_query = "MATCH (a:Assessment) RETURN count(a) as count"
    count_result = db.execute_read(count_query, {})
    print(f"\nTotal assessments in database: {count_result[0]['count']}")

if __name__ == "__main__":
    test_direct_create()
