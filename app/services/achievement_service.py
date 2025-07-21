from app.DB.database import get_database
from app.models.student import Student
from app.models.achievement import Achievement, AchievementMetadata
from app.models.exceptions import (
    DatabaseConnectionError, StudentNotFound, AchievementNotFound,
    InvalidAchievementData, DuplicateAchievementError
)
from typing import Optional, List, Dict, Any
from pymongo.collection import Collection
from datetime import datetime
import uuid

# Obtener la colección de estudiantes
_db = get_database()
students_collection: Optional[Collection] = _db["students"] if _db is not None else None

def _check_db_connection():
    """Check if database connection is available"""
    if students_collection is None:
        raise DatabaseConnectionError("No database connection available")

def update_achievement(email: str, achievement_data: dict, score: float, total_points: float) -> dict:
    """
    Creates or updates an achievement for a student based on score obtained.
    If the score is >= 80% of total, marks the achievement as achieved.
    """
    _check_db_connection()

    if total_points <= 0:
        raise InvalidAchievementData("Total points must be greater than 0")
    
    if score < 0:
        raise InvalidAchievementData("Score cannot be negative")
    
    if score > total_points:
        raise InvalidAchievementData("Score cannot be greater than total points")

    percent = round((score / total_points) * 100, 2)
    achieved = percent >= 80

    # Prepare achievement with new structure
    achievement_data.update({
        "id": str(uuid.uuid4()),
        "email": email,  # Add email to achievement
        "score": score,
        "total_points": total_points,
        "percentage": percent,
        "date_earned": datetime.now() if achieved else None,
        "status": "completed" if achieved else ("in_progress" if percent > 0 else "failed"),
        "achieved": achieved
    })

    # Handle metadata properly
    if "metadata" in achievement_data and achievement_data["metadata"]:
        metadata = AchievementMetadata(**achievement_data["metadata"])
        achievement_data["metadata"] = metadata.dict()

    achievement = Achievement(**achievement_data)

    # Find if student already exists
    student_doc = students_collection.find_one({"email": email})

    if student_doc:
        # Check if already has this achievement
        existing_achievement_index = None
        for i, a in enumerate(student_doc.get("achievements", [])):
            if a["achievement_name"] == achievement.achievement_name:
                existing_achievement_index = i
                break

        if existing_achievement_index is not None:
            # Update existing achievement
            students_collection.update_one(
                {"email": email},
                {
                    "$set": {
                        f"achievements.{existing_achievement_index}": achievement.dict(),
                        "updated_at": datetime.now()
                    }
                }
            )
        else:
            # Add new achievement
            students_collection.update_one(
                {"email": email},
                {
                    "$push": {"achievements": achievement.dict()},
                    "$set": {"updated_at": datetime.now()}
                }
            )
    else:
        # Create student with achievement
        new_student = Student(
            email=email, 
            achievements=[achievement],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        students_collection.insert_one(new_student.dict())

    return {
        "email": email,
        "achievement": achievement.dict(),
        "achieved": achieved,
        "percentage": percent,
        "status": achievement.status
    }

def get_student_achievements(email: str) -> dict:
    """
    Returns a student's achievements by email.
    """
    _check_db_connection()
    
    student = students_collection.find_one({"email": email}, {"_id": 0})
    if not student:
        raise StudentNotFound(f"Student with email {email} not found")
    
    return student

def get_achievement_stats(email: str) -> Dict[str, Any]:
    """Get user's achievement statistics"""
    _check_db_connection()
    
    student_doc = students_collection.find_one({"email": email})
    if not student_doc:
        raise StudentNotFound(f"Student with email {email} not found")
    
    student = Student(**student_doc)
    stats = student.get_achievement_stats()
    return stats.dict()

def get_course_achievements(course_id: str) -> List[Dict[str, Any]]:
    """Get all possible achievements for a course"""
    _check_db_connection()
    
    # This would typically come from a course configuration or master achievement list
    # For now, return achievements that exist in the database for this course
    pipeline = [
        {"$unwind": "$achievements"},
        {"$match": {"achievements.course_id": course_id}},
        {"$group": {
            "_id": "$achievements.achievement_name",
            "title": {"$first": "$achievements.title"},
            "description": {"$first": "$achievements.description"},
            "course_id": {"$first": "$achievements.course_id"},
            "total_earned": {"$sum": {"$cond": ["$achievements.achieved", 1, 0]}},
            "total_attempts": {"$sum": 1}
        }}
    ]
    
    results = list(students_collection.aggregate(pipeline))
    return results

def bulk_update_achievements(updates: List[dict]) -> List[dict]:
    """Update multiple achievements at once"""
    _check_db_connection()
    
    results = []
    for update_data in updates:
        try:
            result = update_achievement(
                email=update_data["email"],
                achievement_data=update_data["achievement"],
                score=update_data["score"],
                total_points=update_data["total_points"]
            )
            results.append({"success": True, "data": result})
        except Exception as e:
            results.append({"success": False, "error": str(e), "email": update_data.get("email")})
    
    return results

def delete_achievement(email: str, achievement_name: str) -> bool:
    """Delete a specific achievement for a student"""
    _check_db_connection()
    
    student = students_collection.find_one({"email": email})
    if not student:
        raise StudentNotFound(f"Student with email {email} not found")
    
    # Check if achievement exists
    achievement_exists = any(
        a["achievement_name"] == achievement_name 
        for a in student.get("achievements", [])
    )
    
    if not achievement_exists:
        raise AchievementNotFound(f"Achievement {achievement_name} not found for student {email}")
    
    # Remove the achievement
    result = students_collection.update_one(
        {"email": email},
        {
            "$pull": {"achievements": {"achievement_name": achievement_name}},
            "$set": {"updated_at": datetime.now()}
        }
    )
    
    return result.modified_count > 0

def get_all_achievements_admin() -> List[Dict[str, Any]]:
    """Get all achievements across all users (admin only)"""
    _check_db_connection()
    
    pipeline = [
        {"$unwind": "$achievements"},
        {"$project": {
            "_id": 0,
            "user_email": "$email",
            "user_name": None,  # Could be enhanced with user names
            "created_at": "$created_at",
            "updated_at": "$updated_at",
            "id": "$achievements.id",
            "email": "$achievements.email",
            "achievement_name": "$achievements.achievement_name",
            "course_id": "$achievements.course_id",
            "title": "$achievements.title",
            "description": "$achievements.description",
            "score": "$achievements.score",
            "total_points": "$achievements.total_points",
            "percentage": "$achievements.percentage",
            "date_earned": "$achievements.date_earned",
            "status": "$achievements.status",
            "achieved": "$achievements.achieved",
            "metadata": "$achievements.metadata"
        }},
        {"$sort": {"date_earned": -1}}  # Most recent first
    ]
    
    results = list(students_collection.aggregate(pipeline))
    return results

def count_user_achievements(email: str) -> int:
    """Count total achievements for a user"""
    _check_db_connection()
    
    student = students_collection.find_one({"email": email})
    if not student:
        return 0
    
    return len(student.get("achievements", []))

def calculate_total_xp(email: str) -> int:
    """Calculate total XP for a user"""
    _check_db_connection()
    
    student_doc = students_collection.find_one({"email": email})
    if not student_doc:
        return 0
    
    student = Student(**student_doc)
    return student.calculate_total_xp()

def calculate_average_score(email: str) -> float:
    """Calculate average score for a user"""
    _check_db_connection()
    
    student = students_collection.find_one({"email": email})
    if not student:
        return 0.0
    
    achievements = student.get("achievements", [])
    scores = [a.get("percentage", 0) for a in achievements if a.get("percentage") is not None]
    
    return sum(scores) / len(scores) if scores else 0.0

def get_recent_achievements(email: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent achievements for a user"""
    _check_db_connection()
    
    student_doc = students_collection.find_one({"email": email})
    if not student_doc:
        return []
    
    student = Student(**student_doc)
    recent = student.get_recent_achievements(limit)
    return [a.dict() for a in recent] 