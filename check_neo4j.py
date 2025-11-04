#!/usr/bin/env python3
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "")

driver = GraphDatabase.driver(uri, auth=(user, password))
database = os.getenv("NEO4J_DATABASE", "kitakyu-facilities")

with driver.session(database=database) as session:
    # Count users
    users_result = session.run("MATCH (u:User) RETURN count(u) as count")
    users_count = users_result.single()["count"]
    print(f"利用者総数: {users_count}件")
    
    # Count assessments
    assessments_result = session.run("MATCH (a:Assessment) RETURN count(a) as count")
    assessments_count = assessments_result.single()["count"]
    print(f"アセスメント総数: {assessments_count}件")
    
    # Count plans
    plans_result = session.run("MATCH (p:Plan) RETURN count(p) as count")
    plans_count = plans_result.single()["count"]
    print(f"計画総数: {plans_count}件")
    
    # Get users with their assessments
    print("\n各利用者のアセスメント状況:")
    users_with_assessments = session.run("""
        MATCH (u:User)
        OPTIONAL MATCH (u)-[:HAS_ASSESSMENT]->(a:Assessment)
        RETURN u.name as name, u.user_id as user_id, 
               collect(a.assessment_id)[0..1] as assessment_ids,
               count(a) as assessment_count
        ORDER BY u.name
    """)
    
    for record in users_with_assessments:
        status = "あり" if record["assessment_count"] > 0 else "なし"
        print(f"  {record['name']}: アセスメント{status} ({record['assessment_count']}件)")
        if record["assessment_ids"]:
            for aid in record["assessment_ids"]:
                if aid:
                    print(f"    - {aid[:12]}...")

driver.close()
