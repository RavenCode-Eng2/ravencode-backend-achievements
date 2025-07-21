"""
Achievement Master Service - Manages achievement definitions and templates
This service handles the master list of achievements that can be earned,
separate from individual student achievement records.
"""

from app.DB.database import get_database
from app.models.achievement import Achievement, AchievementMetadata, AvailableAchievement
from app.models.exceptions import DatabaseConnectionError, AchievementNotFound
from typing import Optional, List, Dict, Any
from pymongo.collection import Collection
from datetime import datetime
import uuid

# Get the achievements master collection
_db = get_database()
achievements_master_collection: Optional[Collection] = _db["achievements_master"] if _db is not None else None

def _check_db_connection():
    """Check if database connection is available"""
    if achievements_master_collection is None:
        raise DatabaseConnectionError("No database connection available")

def create_achievement_template(
    achievement_name: str,
    course_id: str,
    title: str,
    description: str,
    max_points: float = 100.0,
    requirements: Optional[List[str]] = None,
    metadata: Optional[AchievementMetadata] = None
) -> Dict[str, Any]:
    """
    Create a new achievement template that can be earned by students
    """
    _check_db_connection()
    
    # Check if achievement already exists for this course
    existing = achievements_master_collection.find_one({
        "achievement_name": achievement_name,
        "course_id": course_id
    })
    
    if existing:
        raise ValueError(f"Achievement {achievement_name} already exists for course {course_id}")
    
    achievement_template = {
        "id": str(uuid.uuid4()),
        "achievement_name": achievement_name,
        "course_id": course_id,
        "title": title,
        "description": description,
        "max_points": max_points,
        "requirements": requirements or [],
        "metadata": metadata.dict() if metadata else None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "active": True
    }
    
    result = achievements_master_collection.insert_one(achievement_template)
    achievement_template["_id"] = str(result.inserted_id)
    
    return achievement_template

def get_available_achievements_for_course(course_id: str) -> List[AvailableAchievement]:
    """
    Get all available achievement templates for a specific course
    """
    _check_db_connection()
    
    templates = achievements_master_collection.find({
        "course_id": course_id,
        "active": True
    })
    
    available_achievements = []
    for template in templates:
        metadata = None
        if template.get("metadata"):
            metadata = AchievementMetadata(**template["metadata"])
        
        available_achievement = AvailableAchievement(
            achievement_name=template["achievement_name"],
            title=template["title"],
            description=template.get("description"),
            requirements=template.get("requirements", []),
            max_points=template.get("max_points", 100.0),
            category=metadata.category if metadata else None,
            rarity=metadata.rarity if metadata else None,
            metadata=metadata
        )
        available_achievements.append(available_achievement)
    
    return available_achievements

def get_achievement_template(achievement_name: str, course_id: str) -> Dict[str, Any]:
    """
    Get a specific achievement template
    """
    _check_db_connection()
    
    template = achievements_master_collection.find_one({
        "achievement_name": achievement_name,
        "course_id": course_id,
        "active": True
    })
    
    if not template:
        raise AchievementNotFound(f"Achievement template {achievement_name} not found for course {course_id}")
    
    return template

def update_achievement_template(
    achievement_name: str,
    course_id: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update an existing achievement template
    """
    _check_db_connection()
    
    # Don't allow updating the achievement_name or course_id
    forbidden_fields = ["achievement_name", "course_id", "id", "_id", "created_at"]
    for field in forbidden_fields:
        if field in updates:
            del updates[field]
    
    updates["updated_at"] = datetime.now()
    
    result = achievements_master_collection.update_one(
        {
            "achievement_name": achievement_name,
            "course_id": course_id,
            "active": True
        },
        {"$set": updates}
    )
    
    if result.matched_count == 0:
        raise AchievementNotFound(f"Achievement template {achievement_name} not found for course {course_id}")
    
    return get_achievement_template(achievement_name, course_id)

def deactivate_achievement_template(achievement_name: str, course_id: str) -> bool:
    """
    Deactivate an achievement template (soft delete)
    """
    _check_db_connection()
    
    result = achievements_master_collection.update_one(
        {
            "achievement_name": achievement_name,
            "course_id": course_id,
            "active": True
        },
        {
            "$set": {
                "active": False,
                "updated_at": datetime.now()
            }
        }
    )
    
    return result.modified_count > 0

def get_all_achievement_templates() -> List[Dict[str, Any]]:
    """
    Get all achievement templates across all courses (admin function)
    """
    _check_db_connection()
    
    templates = list(achievements_master_collection.find({"active": True}))
    
    # Convert ObjectId to string for JSON serialization
    for template in templates:
        template["_id"] = str(template["_id"])
    
    return templates

def get_achievement_templates_by_course() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get achievement templates grouped by course
    """
    _check_db_connection()
    
    pipeline = [
        {"$match": {"active": True}},
        {"$group": {
            "_id": "$course_id",
            "achievements": {"$push": "$$ROOT"}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    results = list(achievements_master_collection.aggregate(pipeline))
    
    grouped_achievements = {}
    for result in results:
        course_id = result["_id"]
        achievements = result["achievements"]
        
        # Convert ObjectId to string
        for achievement in achievements:
            achievement["_id"] = str(achievement["_id"])
        
        grouped_achievements[course_id] = achievements
    
    return grouped_achievements

def search_achievement_templates(
    query: str,
    course_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search achievement templates by title, description, or achievement_name
    """
    _check_db_connection()
    
    search_filter = {
        "active": True,
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"achievement_name": {"$regex": query, "$options": "i"}}
        ]
    }
    
    if course_id:
        search_filter["course_id"] = course_id
    
    templates = list(achievements_master_collection.find(search_filter))
    
    # Convert ObjectId to string
    for template in templates:
        template["_id"] = str(template["_id"])
    
    return templates 