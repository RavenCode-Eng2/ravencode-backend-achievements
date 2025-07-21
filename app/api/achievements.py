from fastapi import APIRouter, HTTPException, Query
from pydantic import EmailStr
from typing import Optional, List, Dict, Any
from app.services.achievement_service import (
    update_achievement, get_student_achievements, get_achievement_stats,
    get_course_achievements, bulk_update_achievements, delete_achievement,
    get_all_achievements_admin
)
from app.services.achievement_master_service import (
    get_available_achievements_for_course, create_achievement_template,
    get_all_achievement_templates
)
from app.models import StandardResponse
from app.models.achievement import (
    AchievementUpdateRequest, BulkUpdateRequest, UserAchievementResponse,
    AdminAchievementRecord, CreateAchievementRequest, AvailableAchievement,
    AchievementStats, Achievement, AchievementMetadata
)
from app.models.student import Student
from app.models.exceptions import (
    AchievementError, AchievementNotFound, StudentNotFound,
    InvalidAchievementData, DatabaseConnectionError
)

router = APIRouter(prefix="/achievements", tags=["Achievements"])

@router.post(
    "/update",
    summary="Create or update student achievement",
    description="Creates a new achievement or updates an existing one for a student",
    response_description="Achievement update result"
)
async def update_student_achievement(request: AchievementUpdateRequest):
    try:
        result = update_achievement(
            email=request.email,
            achievement_data=request.achievement.dict(),
            score=request.score,
            total_points=request.total_points
        )
        
        return StandardResponse.success_response(
            data=result,
            message="Achievement updated successfully"
        )
    except AchievementError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get(
    "/{email}",
    summary="Get student achievements",
    description="Retrieves all achievements for a specific student",
    response_model=StandardResponse
)
async def get_achievements(email: EmailStr):
    try:
        student_data = get_student_achievements(email)
        student = Student(**student_data)
        
        # Return in the format expected by frontend (UserAchievementResponse)
        response_data = UserAchievementResponse(
            email=email,
            achievements=student.achievements
        )
        
        return StandardResponse.success_response(
            data=response_data.dict(),
            message="Student achievements retrieved successfully"
        )
    except StudentNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get(
    "/{email}/stats",
    summary="Get achievement statistics for a student",
    description="Retrieves detailed achievement statistics for a student",
    response_model=StandardResponse
)
async def get_achievement_statistics(email: EmailStr):
    try:
        student_data = get_student_achievements(email)
        student = Student(**student_data)
        
        # Calculate statistics using the student model method
        stats = student.get_achievement_stats()
        
        return StandardResponse.success_response(
            data=stats.dict(),
            message="Achievement statistics retrieved successfully"
        )
    except StudentNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get(
    "/course/{course_id}/available",
    summary="Get available achievements for a course",
    description="Retrieves all possible achievements for a specific course from the master achievement list",
    response_model=StandardResponse
)
async def get_available_achievements(course_id: str):
    try:
        # Use the master achievement service to get properly structured data
        available_achievements = get_available_achievements_for_course(course_id)
        
        # Convert to dict format for response
        achievements_data = [achievement.dict() for achievement in available_achievements]
        
        return StandardResponse.success_response(
            data=achievements_data,
            message=f"Available achievements for course {course_id} retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post(
    "/bulk-update",
    summary="Bulk update achievements",
    description="Updates multiple achievements at once",
    response_model=StandardResponse
)
async def bulk_update_achievements_endpoint(request: BulkUpdateRequest):
    try:
        # Convert to the format expected by the service
        updates = []
        for update_req in request.updates:
            updates.append({
                "email": update_req.email,
                "achievement": update_req.achievement.dict(),
                "score": update_req.score,
                "total_points": update_req.total_points
            })
        
        results = bulk_update_achievements(updates)
        
        # Count successes and failures
        successes = sum(1 for r in results if r.get("success"))
        failures = len(results) - successes
        
        return StandardResponse.success_response(
            data={
                "results": results,
                "summary": {
                    "total": len(results),
                    "successful": successes,
                    "failed": failures
                }
            },
            message=f"Bulk update completed: {successes} successful, {failures} failed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.delete(
    "/{email}/{achievement_name}",
    summary="Delete specific achievement",
    description="Deletes a specific achievement for a student",
    response_model=StandardResponse
)
async def delete_achievement_endpoint(email: EmailStr, achievement_name: str):
    try:
        success = delete_achievement(email, achievement_name)
        
        return StandardResponse.success_response(
            data={"deleted": success, "email": email, "achievement_name": achievement_name},
            message=f"Achievement {achievement_name} deleted successfully" if success else "Achievement not found"
        )
    except AchievementNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# ============================
# ACHIEVEMENT TEMPLATE MANAGEMENT
# ============================

@router.post(
    "/templates",
    summary="Create achievement template",
    description="Creates a new achievement template that can be earned by students",
    response_model=StandardResponse
)
async def create_achievement_template_endpoint(
    achievement_name: str,
    course_id: str,
    title: str,
    description: str,
    max_points: float = 100.0,
    requirements: Optional[List[str]] = None,
    metadata: Optional[AchievementMetadata] = None
):
    try:
        template = create_achievement_template(
            achievement_name=achievement_name,
            course_id=course_id,
            title=title,
            description=description,
            max_points=max_points,
            requirements=requirements,
            metadata=metadata
        )
        
        return StandardResponse.success_response(
            data=template,
            message=f"Achievement template '{title}' created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get(
    "/templates",
    summary="Get all achievement templates",
    description="Retrieves all achievement templates (admin function)",
    response_model=StandardResponse
)
async def get_all_achievement_templates_endpoint():
    try:
        templates = get_all_achievement_templates()
        
        return StandardResponse.success_response(
            data=templates,
            message="All achievement templates retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# ============================
# ADMIN ENDPOINTS
# ============================

admin_router = APIRouter(prefix="/admin/achievements", tags=["Admin - Achievements"])

@admin_router.get(
    "",
    summary="Get all achievements (Admin)",
    description="Gets all achievements across all users (admin only)",
    response_model=StandardResponse
)
async def get_all_achievements_admin_endpoint():
    try:
        all_achievements = get_all_achievements_admin()
        
        return StandardResponse.success_response(
            data=all_achievements,
            message="All achievements retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@admin_router.get(
    "/user/{email}",
    summary="Get achievements for user (Admin view)",
    description="Gets all achievements for a specific user (admin view with additional fields)",
    response_model=StandardResponse
)
async def get_user_achievements_admin(email: EmailStr):
    try:
        student_data = get_student_achievements(email)
        student = Student(**student_data)
        
        # Convert to AdminAchievementRecord format
        admin_achievements = []
        for achievement in student.achievements:
            admin_record = AdminAchievementRecord(
                **achievement.dict(),
                user_email=email,
                user_name=None,  # Could be enhanced to include user name
                created_at=student.created_at,
                updated_at=student.updated_at
            )
            admin_achievements.append(admin_record.dict())
        
        return StandardResponse.success_response(
            data=admin_achievements,
            message=f"Achievements for user {email} retrieved successfully (admin view)"
        )
    except StudentNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@admin_router.post(
    "/create",
    summary="Create achievement (Admin)",
    description="Creates an achievement for a user (admin interface)",
    response_model=StandardResponse
)
async def create_achievement_admin(request: CreateAchievementRequest):
    try:
        # Convert CreateAchievementRequest to AchievementUpdateRequest
        achievement_update = AchievementUpdateRequest(
            email=request.user_email,
            achievement={
                "achievement_name": request.achievement_name,
                "course_id": request.course_id,
                "title": request.title,
                "description": request.description,
                "metadata": request.metadata.dict() if request.metadata else None
            },
            score=request.score,
            total_points=request.total_points
        )
        
        result = update_achievement(
            email=achievement_update.email,
            achievement_data=achievement_update.achievement.dict(),
            score=achievement_update.score,
            total_points=achievement_update.total_points
        )
        
        return StandardResponse.success_response(
            data=result,
            message="Achievement created successfully (admin)"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Include admin router in the main router
router.include_router(admin_router) 