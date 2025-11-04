#!/usr/bin/env python3
"""
Test user management API.
"""
import requests
import json
from datetime import date

API_BASE = "http://localhost:8001/api"


def test_create_user():
    """Test creating a new user."""
    print("\n=== Test: Create User ===")

    user_data = {
        "name": "山田太郎",
        "kana": "ヤマダタロウ",
        "birth_date": "1980-05-15",
        "gender": "男性",
        "disability_type": "知的障害",
        "disability_grade": "重度",
        "support_level": "区分4",
        "therapy_notebook": True,
        "medical_care_needs": False,
        "behavioral_support_needs": False,
        "living_situation": "在宅",
        "family_structure": "本人、母",
        "guardian_name": "山田花子",
        "guardian_relation": "母",
        "contact_phone": "090-1234-5678",
        "contact_address": "北九州市小倉北区",
    }

    response = requests.post(f"{API_BASE}/users", json=user_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 201:
        user = response.json()
        print(f"Created user: {user['name']} (ID: {user['user_id']})")
        print(f"Age: {user['age']}")
        return user["user_id"]
    else:
        print(f"Error: {response.text}")
        return None


def test_list_users():
    """Test listing users."""
    print("\n=== Test: List Users ===")

    response = requests.get(f"{API_BASE}/users")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Total users: {data['total']}")
        print(f"Page {data['page']}, showing {len(data['users'])} users")
        for user in data["users"]:
            print(f"  - {user['name']} ({user['age']}歳, {user['disability_type']})")
    else:
        print(f"Error: {response.text}")


def test_get_user(user_id):
    """Test getting a specific user."""
    print(f"\n=== Test: Get User {user_id} ===")

    response = requests.get(f"{API_BASE}/users/{user_id}")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        user = response.json()
        print(f"Name: {user['name']}")
        print(f"Birth date: {user['birth_date']}, Age: {user['age']}")
        print(f"Disability: {user['disability_type']} ({user['disability_grade']})")
        print(f"Support level: {user['support_level']}")
        print(f"Guardian: {user['guardian_name']} ({user['guardian_relation']})")
    else:
        print(f"Error: {response.text}")


def test_update_user(user_id):
    """Test updating a user."""
    print(f"\n=== Test: Update User {user_id} ===")

    update_data = {"support_level": "区分5", "living_situation": "グループホーム"}

    response = requests.put(f"{API_BASE}/users/{user_id}", json=update_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        user = response.json()
        print(f"Updated support_level: {user['support_level']}")
        print(f"Updated living_situation: {user['living_situation']}")
    else:
        print(f"Error: {response.text}")


def test_search_users():
    """Test searching users."""
    print("\n=== Test: Search Users ===")

    response = requests.get(f"{API_BASE}/users", params={"search_query": "山田"})
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total']} users matching '山田'")
        for user in data["users"]:
            print(f"  - {user['name']}")
    else:
        print(f"Error: {response.text}")


def test_delete_user(user_id):
    """Test deleting a user."""
    print(f"\n=== Test: Delete User {user_id} ===")

    response = requests.delete(f"{API_BASE}/users/{user_id}")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Message: {data['message']}")
    else:
        print(f"Error: {response.text}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("User API Tests")
    print("=" * 60)

    # Create user
    user_id = test_create_user()

    if user_id:
        # List users
        test_list_users()

        # Get user
        test_get_user(user_id)

        # Update user
        test_update_user(user_id)

        # Get updated user
        test_get_user(user_id)

        # Search users
        test_search_users()

        # Delete user
        # test_delete_user(user_id)  # Commented out to keep test data

    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
