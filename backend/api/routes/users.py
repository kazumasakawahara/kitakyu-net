# -*- coding: utf-8 -*-
"""
User management API routes.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from backend.api.models.user import (
    User,
    UserCreate,
    UserUpdate,
    UserList,
    UserFilter,
    UserDeleteResponse,
)
from backend.services.user_service import get_user_service
from backend.services.assessment_service import get_assessment_service
from backend.services.user_detail_service import get_user_detail_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=User, status_code=201)
async def create_user(user_data: UserCreate):
    """
    Create new user.

    Args:
        user_data: User data

    Returns:
        Created user
    """
    try:
        service = get_user_service()
        user = service.create_user(user_data.model_dump())
        return user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=UserList)
async def list_users(
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="ページサイズ"),
    disability_type: Optional[str] = Query(None, description="障害種別フィルター"),
    support_level: Optional[str] = Query(None, description="支援区分フィルター"),
    age_min: Optional[int] = Query(None, ge=0, description="最小年齢"),
    age_max: Optional[int] = Query(None, le=120, description="最大年齢"),
    living_situation: Optional[str] = Query(None, description="居住状況フィルター"),
    search_query: Optional[str] = Query(None, description="名前・カナ検索"),
):
    """
    List users with pagination and filtering.

    Args:
        page: Page number
        page_size: Page size
        disability_type: Filter by disability type
        support_level: Filter by support level
        age_min: Minimum age
        age_max: Maximum age
        living_situation: Filter by living situation
        search_query: Search by name or kana

    Returns:
        List of users with pagination
    """
    try:
        service = get_user_service()

        filters = {}
        if disability_type:
            filters["disability_type"] = disability_type
        if support_level:
            filters["support_level"] = support_level
        if age_min is not None:
            filters["age_min"] = age_min
        if age_max is not None:
            filters["age_max"] = age_max
        if living_situation:
            filters["living_situation"] = living_situation
        if search_query:
            filters["search_query"] = search_query

        result = service.list_users(page=page, page_size=page_size, filters=filters)
        return result
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    """
    Get user by ID.

    Args:
        user_id: User ID

    Returns:
        User data
    """
    try:
        service = get_user_service()
        user = service.get_user(user_id)

        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, update_data: UserUpdate):
    """
    Update user.

    Args:
        user_id: User ID
        update_data: Fields to update

    Returns:
        Updated user
    """
    try:
        service = get_user_service()

        # Remove None values
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

        if not update_dict:
            raise HTTPException(status_code=400, detail="No fields to update")

        user = service.update_user(user_id, update_dict)

        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", response_model=UserDeleteResponse)
async def delete_user(user_id: str):
    """
    Delete user (soft delete).

    Args:
        user_id: User ID

    Returns:
        Deletion confirmation
    """
    try:
        service = get_user_service()
        deleted = service.delete_user(user_id)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        return {
            "status": "deleted",
            "user_id": user_id,
            "message": f"User {user_id} has been deleted",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/detail")
async def get_user_detail(user_id: str):
    """
    Get comprehensive user detail with support information.

    Args:
        user_id: User ID

    Returns:
        User detail with services, monitoring, goals, timeline, and alerts
    """
    try:
        service = get_user_detail_service()
        detail = service.get_user_detail(user_id)

        if not detail:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        return detail
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user detail for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/assessments")
async def list_user_assessments(user_id: str):
    """
    Get all assessments for a user.

    Args:
        user_id: User ID

    Returns:
        List of assessments
    """
    try:
        # First verify user exists
        user_service = get_user_service()
        user = user_service.get_user(user_id)

        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        # Get assessments
        assessment_service = get_assessment_service()
        assessments = assessment_service.list_user_assessments(user_id)

        return assessments
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting assessments for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
