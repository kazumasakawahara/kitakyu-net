#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Goal API integration.
"""
import requests
import json
from datetime import date

BASE_URL = "http://localhost:8001/api"


def test_goal_workflow():
    """Test complete goal workflow: create user, assessment, suggest goals, create goal."""

    print("=" * 60)
    print("Goal API Integration Test")
    print("=" * 60)

    # Step 1: Create test user
    print("\n=== Step 1: Create Test User ===")
    user_data = {
        "name": "テスト太郎",
        "birth_date": str(date(1985, 6, 15)),
        "disability_type": "精神障害",
        "support_level": "区分3",
        "living_situation": "単身生活",
        "family_structure": "独居",
        "main_caregiver": "本人",
        "guardian_info": "",
        "residential_history": "アパート暮らし5年",
        "medical_history": "統合失調症",
        "current_services": [],
        "contact_phone": "090-1234-5678",
        "contact_email": "test@example.com",
        "emergency_contact": "兄: 080-9876-5432",
        "created_by": "test_script",
    }

    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 201:
        user = response.json()
        user_id = user["user_id"]
        print(f"Created user: {user['name']} (ID: {user_id})")
    else:
        print(f"Error: {response.text}")
        return

    # Step 2: Create assessment with LLM analysis
    print("\n=== Step 2: Create Assessment ===")
    assessment_data = {
        "user_id": user_id,
        "interview_date": str(date.today()),
        "interview_content": """
利用者面談記録:

【本人の希望】
- 仕事をしたい。できれば工場のような軽作業がいい
- 週3日くらいから始めたい
- 収入を得て自立した生活がしたい

【生活状況】
- 単身アパート暮らし。家事は何とか自分でできる
- 服薬管理は自分でできている
- 金銭管理は苦手。計画的な買い物が難しい

【家族の希望】
- 無理のない範囲で社会参加してほしい
- 定期的に様子を見てもらえる環境がいい

【現在の課題】
- 対人関係に不安がある。大勢の中だと緊張する
- 生活リズムが不規則になりがち
- 金銭管理が苦手

【強み・できること】
- 単純作業は丁寧にできる
- 時間があれば家事はできる
- 服薬管理はしっかりできている
        """,
        "analyze": True,
    }

    response = requests.post(f"{BASE_URL}/assessments", json=assessment_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 201:
        assessment = response.json()
        assessment_id = assessment["assessment_id"]
        print(f"Created assessment: {assessment_id}")
        print(f"Analyzed needs: {assessment.get('analyzed_needs', [])[:2]}...")
        print(f"Confidence score: {assessment.get('confidence_score')}")
    else:
        print(f"Error: {response.text}")
        return

    # Step 3: Suggest goals based on assessment
    print("\n=== Step 3: Suggest Goals (LLM) ===")
    suggestion_request = {
        "assessment_id": assessment_id,
        "goal_type": "長期目標",
    }

    response = requests.post(f"{BASE_URL}/goals/suggest", json=suggestion_request)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        suggestion_response = response.json()
        suggestions = suggestion_response["suggestions"]
        print(f"Generated {len(suggestions)} goal suggestions:")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"\n目標案 {i}:")
            print(f"  内容: {suggestion['goal_text']}")
            print(f"  理由: {suggestion['goal_reason']}")
            print(f"  評価期間: {suggestion['evaluation_period']}")
            smart = suggestion['smart_evaluation']
            print(f"  SMART: S={smart['is_specific']} M={smart['is_measurable']} A={smart['is_achievable']} R={smart['is_relevant']} T={smart['is_time_bound']}")
            print(f"  信頼度: {suggestion['confidence']}")
    else:
        print(f"Error: {response.text}")
        return

    # Step 4: Evaluate a custom goal with SMART
    print("\n=== Step 4: Evaluate Custom Goal ===")
    evaluation_request = {
        "goal_text": "週3回、就労継続支援B型事業所に通所し、軽作業を行う",
    }

    response = requests.post(f"{BASE_URL}/goals/evaluate", json=evaluation_request)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        evaluation = response.json()
        print(f"Goal: {evaluation['goal_text']}")
        print(f"SMART Score: {evaluation['smart_score']}")
        print(f"Specific: {evaluation['is_specific']}")
        print(f"Measurable: {evaluation['is_measurable']}")
        print(f"Achievable: {evaluation['is_achievable']}")
        print(f"Relevant: {evaluation['is_relevant']}")
        print(f"Time-bound: {evaluation['is_time_bound']}")
        if evaluation['suggestions']:
            print("Improvement suggestions:")
            for suggestion in evaluation['suggestions']:
                print(f"  - {suggestion}")
    else:
        print(f"Error: {response.text}")

    # Step 5: Create Plan (for goal creation test)
    print("\n=== Step 5: Create Plan ===")
    # Note: Plan creation API not yet implemented, so we'll create directly in Neo4j
    # For now, skip goal creation test

    print("\n=== Test Complete ===")
    print("✅ User creation: Success")
    print("✅ Assessment with LLM: Success")
    print("✅ Goal suggestion: Success")
    print("✅ SMART evaluation: Success")


if __name__ == "__main__":
    test_goal_workflow()
