from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CategoryEnum(str, Enum):
    learning = "learning"
    practice = "practice"
    achievement = "achievement"
    mastery = "mastery"
    dedication = "dedication"
    community = "community"

class RarityEnum(str, Enum):
    common = "common"
    rare = "rare"
    epic = "epic"
    legendary = "legendary"

class DifficultyEnum(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"

class StatusEnum(str, Enum):
    completed = "completed"
    in_progress = "in_progress"
    failed = "failed"
    pending = "pending"

class AchievementMetadata(BaseModel):
    """Metadata structure for achievements matching frontend interface"""
    category: Optional[CategoryEnum] = None
    rarity: Optional[RarityEnum] = None
    xp_reward: Optional[int] = Field(None, description="Experience points awarded")
    difficulty: Optional[DifficultyEnum] = None
    module: Optional[str] = Field(None, description="Specific module/lesson within course")
    icon_url: Optional[str] = Field(None, description="Custom icon URL for the achievement")
    requirements: Optional[List[str]] = Field(None, description="List of requirements to earn this achievement")
    tags: Optional[List[str]] = Field(None, description="Additional categorization tags")
    
    # Allow additional custom fields
    class Config:
        extra = "allow"

class Achievement(BaseModel):
    """Achievement record matching frontend ApiAchievementRecord interface"""
    id: Optional[str] = None
    email: EmailStr = Field(..., description="User email - links achievement to user")
    achievement_name: str = Field(..., description="Unique identifier for the achievement type")
    course_id: str = Field(..., description="Course this achievement belongs to")
    title: str = Field(..., description="Display title")
    description: Optional[str] = Field(None, description="Achievement description")
    score: float = Field(..., description="Points scored by user")
    total_points: float = Field(..., description="Maximum possible points")
    percentage: Optional[float] = Field(None, description="Calculated percentage (score/total_points * 100)")
    date_earned: Optional[datetime] = Field(None, description="ISO date when achievement was earned")
    status: Optional[StatusEnum] = Field(StatusEnum.pending, description="Achievement status")
    achieved: Optional[bool] = Field(False, description="Whether the achievement has been earned")
    metadata: Optional[AchievementMetadata] = Field(None, description="Additional achievement data")
    
    @validator('percentage', always=True)
    def calculate_percentage(cls, v, values):
        """Auto-calculate percentage if score and total_points are provided"""
        if v is None and 'score' in values and 'total_points' in values:
            score = values.get('score')
            total_points = values.get('total_points')
            if score is not None and total_points is not None and total_points > 0:
                return round((score / total_points) * 100, 2)
        return v
    
    @validator('achieved', always=True)
    def determine_achieved(cls, v, values):
        """Auto-determine achieved status based on percentage"""
        percentage = values.get('percentage')
        if percentage is not None and percentage >= 80:
            return True
        return v
    
    @validator('status', always=True)
    def set_status_based_on_achieved(cls, v, values):
        """Set status based on achieved and percentage"""
        achieved = values.get('achieved', False)
        percentage = values.get('percentage')
        
        if achieved and percentage is not None and percentage >= 80:
            return StatusEnum.completed
        elif percentage is not None and percentage > 0:
            return StatusEnum.in_progress
        elif percentage is not None and percentage == 0:
            return StatusEnum.failed
        return v or StatusEnum.pending
    
    @validator('date_earned', always=True)
    def set_date_earned(cls, v, values):
        """Set date_earned when achievement is achieved"""
        achieved = values.get('achieved', False)
        if achieved and v is None:
            return datetime.now()
        elif not achieved:
            return None
        return v

class AchievementStats(BaseModel):
    """Achievement statistics matching frontend interface"""
    total_achievements: int = Field(..., description="Total achievements earned")
    total_xp: int = Field(..., description="Total XP earned from achievements")
    average_score: float = Field(..., description="Average percentage across all achievements")
    achievements_by_course: Dict[str, int] = Field(..., description="Count per course")
    recent_achievements: List[Achievement] = Field(..., description="Recently earned achievements")
    completion_rate: Optional[float] = Field(None, description="Overall completion percentage")
    streak_count: Optional[int] = Field(None, description="Current achievement streak")
    best_category: Optional[str] = Field(None, description="Category with most achievements")

class AchievementInput(BaseModel):
    """Achievement input structure matching frontend interface"""
    achievement_name: str = Field(..., description="Unique identifier")
    course_id: str = Field(..., description="Course association")
    title: str = Field(..., description="Display title")
    description: Optional[str] = Field(None, description="Description")
    metadata: Optional[AchievementMetadata] = Field(None, description="Additional data")

class AchievementUpdateRequest(BaseModel):
    """Request to create/update an achievement matching frontend interface"""
    email: EmailStr = Field(..., description="User email")
    achievement: AchievementInput = Field(..., description="Achievement definition")
    score: float = Field(..., description="User's score")
    total_points: float = Field(..., description="Maximum possible points")

class BulkUpdateRequest(BaseModel):
    """Bulk update request for multiple achievements"""
    updates: List[AchievementUpdateRequest] = Field(..., description="Array of achievement updates")

class AvailableAchievement(BaseModel):
    """Available achievement template matching frontend interface"""
    achievement_name: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Display title")
    description: Optional[str] = Field(None, description="Description")
    requirements: Optional[List[str]] = Field(None, description="What user needs to do")
    max_points: float = Field(..., description="Maximum points possible")
    category: Optional[CategoryEnum] = Field(None, description="Achievement category")
    rarity: Optional[RarityEnum] = Field(None, description="Rarity level")
    metadata: Optional[AchievementMetadata] = Field(None, description="Additional metadata")

class UserAchievementResponse(BaseModel):
    """User achievement data response matching frontend interface"""
    email: EmailStr = Field(..., description="User email")
    achievements: List[Achievement] = Field(..., description="All achievements for this user")
    stats: Optional[AchievementStats] = Field(None, description="Optional statistics")

class AdminAchievementRecord(Achievement):
    """Admin-specific achievement record with additional fields"""
    user_name: Optional[str] = Field(None, description="User's display name")
    user_email: EmailStr = Field(..., description="User's email (explicit)")
    created_at: Optional[datetime] = Field(None, description="When achievement record was created")
    updated_at: Optional[datetime] = Field(None, description="When achievement was last updated")

class CreateAchievementRequest(BaseModel):
    """Request to create achievement for admin panel"""
    user_email: EmailStr = Field(..., description="Target user")
    course_id: str = Field(..., description="Course association")
    achievement_name: str = Field(..., description="Achievement identifier")
    title: str = Field(..., description="Display title")
    description: str = Field(..., description="Description")
    score: float = Field(..., description="User's score")
    total_points: float = Field(..., description="Maximum points")
    metadata: Optional[AchievementMetadata] = Field(None, description="Additional data") 