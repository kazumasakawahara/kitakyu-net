# -*- coding: utf-8 -*-
"""
User management service.

Handles CRUD operations for User nodes in Neo4j.
"""
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from loguru import logger

from backend.neo4j.client import get_neo4j_client


class UserService:
    """Service for managing users."""

    def __init__(self):
        """Initialize user service."""
        self.db = get_neo4j_client()

    def calculate_age(self, birth_date: date) -> int:
        """Calculate age from birth date."""
        today = date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new user.

        Args:
            user_data: User data dict

        Returns:
            Created user dict with user_id
        """
        user_id = str(uuid.uuid4())
        now = datetime.now()

        # Calculate age
        if "birth_date" in user_data and isinstance(user_data["birth_date"], date):
            age = self.calculate_age(user_data["birth_date"])
        else:
            age = None

        # Convert date to ISO string for Neo4j
        if "birth_date" in user_data and isinstance(user_data["birth_date"], date):
            user_data["birth_date"] = user_data["birth_date"].isoformat()

        # Convert mental health notebook expiry date if present
        if "mental_health_notebook_expiry" in user_data and isinstance(user_data["mental_health_notebook_expiry"], date):
            user_data["mental_health_notebook_expiry"] = user_data["mental_health_notebook_expiry"].isoformat()

        query = """
        CREATE (u:User {
            user_id: $user_id,
            name: $name,
            kana: $kana,
            birth_date: date($birth_date),
            age: $age,
            gender: $gender,
            disability_type: $disability_type,
            disability_grade: $disability_grade,
            support_level: $support_level,
            therapy_notebook: $therapy_notebook,
            therapy_notebook_grade: $therapy_notebook_grade,
            mental_health_notebook: $mental_health_notebook,
            mental_health_notebook_grade: $mental_health_notebook_grade,
            mental_health_notebook_expiry: CASE WHEN $mental_health_notebook_expiry IS NOT NULL THEN date($mental_health_notebook_expiry) ELSE NULL END,
            medical_care_needs: $medical_care_needs,
            behavioral_support_needs: $behavioral_support_needs,
            living_situation: $living_situation,
            family_structure: $family_structure,
            guardian_name: $guardian_name,
            guardian_relation: $guardian_relation,
            contact_phone: $contact_phone,
            contact_address: $contact_address,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at)
        })
        RETURN u
        """

        params = {
            "user_id": user_id,
            "age": age,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            **user_data,
        }

        try:
            result = self.db.execute_query(query, params)
            if result:
                user_node = result[0]["u"]
                created_user = dict(user_node)

                # Convert Neo4j types to Python types
                if "birth_date" in created_user:
                    created_user["birth_date"] = (
                        created_user["birth_date"].to_native().isoformat()
                    )
                if "mental_health_notebook_expiry" in created_user and created_user["mental_health_notebook_expiry"]:
                    created_user["mental_health_notebook_expiry"] = (
                        created_user["mental_health_notebook_expiry"].to_native().isoformat()
                    )
                if "created_at" in created_user:
                    created_user["created_at"] = (
                        created_user["created_at"].iso_format()
                        if hasattr(created_user["created_at"], "iso_format")
                        else str(created_user["created_at"])
                    )
                if "updated_at" in created_user:
                    created_user["updated_at"] = (
                        created_user["updated_at"].iso_format()
                        if hasattr(created_user["updated_at"], "iso_format")
                        else str(created_user["updated_at"])
                    )

                logger.success(f"Created user: {user_id}")
                return created_user
            else:
                raise Exception("Failed to create user")

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User dict or None if not found
        """
        query = """
        MATCH (u:User {user_id: $user_id})
        WHERE (u.deleted IS NULL OR u.deleted = false)
        RETURN u
        """

        try:
            result = self.db.execute_query(query, {"user_id": user_id})
            if result:
                user_node = result[0]["u"]
                user = dict(user_node)

                # Convert Neo4j types
                if "birth_date" in user:
                    user["birth_date"] = user["birth_date"].to_native().isoformat()
                if "mental_health_notebook_expiry" in user and user["mental_health_notebook_expiry"]:
                    user["mental_health_notebook_expiry"] = user["mental_health_notebook_expiry"].to_native().isoformat()
                if "created_at" in user:
                    user["created_at"] = (
                        user["created_at"].iso_format()
                        if hasattr(user["created_at"], "iso_format")
                        else str(user["created_at"])
                    )
                if "updated_at" in user:
                    user["updated_at"] = (
                        user["updated_at"].iso_format()
                        if hasattr(user["updated_at"], "iso_format")
                        else str(user["updated_at"])
                    )

                return user
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise

    def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        List users with pagination and filtering.

        Args:
            page: Page number (1-indexed)
            page_size: Number of users per page
            filters: Optional filters

        Returns:
            Dict with users list and pagination info
        """
        conditions = []
        params = {}

        if filters:
            if filters.get("disability_type"):
                conditions.append("u.disability_type = $disability_type")
                params["disability_type"] = filters["disability_type"]

            if filters.get("support_level"):
                conditions.append("u.support_level = $support_level")
                params["support_level"] = filters["support_level"]

            if filters.get("age_min"):
                conditions.append("u.age >= $age_min")
                params["age_min"] = filters["age_min"]

            if filters.get("age_max"):
                conditions.append("u.age <= $age_max")
                params["age_max"] = filters["age_max"]

            if filters.get("living_situation"):
                conditions.append("u.living_situation = $living_situation")
                params["living_situation"] = filters["living_situation"]

            if filters.get("search_query"):
                conditions.append(
                    "(u.name CONTAINS $search_query OR u.kana CONTAINS $search_query)"
                )
                params["search_query"] = filters["search_query"]

        # 削除されていないユーザーのみを対象とする条件を追加
        conditions.append("(u.deleted IS NULL OR u.deleted = false)")

        where_clause = " AND ".join(conditions) if conditions else "true"

        # Count total
        count_query = f"""
        MATCH (u:User)
        WHERE {where_clause}
        RETURN count(u) as total
        """

        total = self.db.execute_query(count_query, params)[0]["total"]

        # Get paginated results
        skip = (page - 1) * page_size
        params["skip"] = skip
        params["limit"] = page_size

        list_query = f"""
        MATCH (u:User)
        WHERE {where_clause}
        RETURN u
        ORDER BY u.name
        SKIP $skip
        LIMIT $limit
        """

        try:
            result = self.db.execute_query(list_query, params)
            users = []

            for record in result:
                user_node = record["u"]
                user = dict(user_node)

                # Convert Neo4j types
                if "birth_date" in user:
                    user["birth_date"] = user["birth_date"].to_native().isoformat()
                if "mental_health_notebook_expiry" in user and user["mental_health_notebook_expiry"]:
                    user["mental_health_notebook_expiry"] = user["mental_health_notebook_expiry"].to_native().isoformat()
                if "created_at" in user:
                    user["created_at"] = (
                        user["created_at"].iso_format()
                        if hasattr(user["created_at"], "iso_format")
                        else str(user["created_at"])
                    )
                if "updated_at" in user:
                    user["updated_at"] = (
                        user["updated_at"].iso_format()
                        if hasattr(user["updated_at"], "iso_format")
                        else str(user["updated_at"])
                    )

                users.append(user)

            return {"users": users, "total": total, "page": page, "page_size": page_size}

        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise

    def update_user(
        self, user_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update user.

        Args:
            user_id: User ID
            update_data: Fields to update

        Returns:
            Updated user dict or None if not found
        """
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if not update_data:
            return self.get_user(user_id)

        # Convert date to ISO string if present
        if "birth_date" in update_data and isinstance(update_data["birth_date"], date):
            update_data["birth_date"] = update_data["birth_date"].isoformat()
            # Recalculate age
            update_data["age"] = self.calculate_age(
                date.fromisoformat(update_data["birth_date"])
            )

        # Convert mental health notebook expiry date if present
        if "mental_health_notebook_expiry" in update_data and isinstance(update_data["mental_health_notebook_expiry"], date):
            update_data["mental_health_notebook_expiry"] = update_data["mental_health_notebook_expiry"].isoformat()

        # Build SET clause
        set_clauses = []
        for key in update_data.keys():
            if key == "mental_health_notebook_expiry":
                # Handle date type with CASE statement
                set_clauses.append(f"u.{key} = CASE WHEN ${key} IS NOT NULL THEN date(${key}) ELSE NULL END")
            else:
                set_clauses.append(f"u.{key} = ${key}")
        set_clauses.append("u.updated_at = datetime($updated_at)")

        query = f"""
        MATCH (u:User {{user_id: $user_id}})
        SET {', '.join(set_clauses)}
        RETURN u
        """

        params = {
            "user_id": user_id,
            "updated_at": datetime.now().isoformat(),
            **update_data,
        }

        try:
            result = self.db.execute_query(query, params)
            if result:
                user_node = result[0]["u"]
                user = dict(user_node)

                # Convert Neo4j types
                if "birth_date" in user:
                    user["birth_date"] = user["birth_date"].to_native().isoformat()
                if "mental_health_notebook_expiry" in user and user["mental_health_notebook_expiry"]:
                    user["mental_health_notebook_expiry"] = user["mental_health_notebook_expiry"].to_native().isoformat()
                if "created_at" in user:
                    user["created_at"] = (
                        user["created_at"].iso_format()
                        if hasattr(user["created_at"], "iso_format")
                        else str(user["created_at"])
                    )
                if "updated_at" in user:
                    user["updated_at"] = (
                        user["updated_at"].iso_format()
                        if hasattr(user["updated_at"], "iso_format")
                        else str(user["updated_at"])
                    )

                logger.success(f"Updated user: {user_id}")
                return user
            else:
                return None

        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    def delete_user(self, user_id: str) -> bool:
        """
        Soft delete user (mark as deleted).

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        query = """
        MATCH (u:User {user_id: $user_id})
        SET u.deleted = true,
            u.deleted_at = datetime($deleted_at)
        RETURN u
        """

        params = {"user_id": user_id, "deleted_at": datetime.now().isoformat()}

        try:
            result = self.db.execute_query(query, params)
            if result:
                logger.success(f"Deleted user: {user_id}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise


# Global service instance
_user_service = None


def get_user_service() -> UserService:
    """Get or create user service instance."""
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service
