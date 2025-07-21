from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from app.models.achievement import Achievement, AchievementStats

class Student(BaseModel):
    """Student model - represents a user in the system"""
    email: EmailStr = Field(..., description="Student email")
    achievements: List[Achievement] = Field(default_factory=list, description="List of student achievements")
    total_xp: Optional[int] = Field(0, ge=0, description="Total experience points")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Account creation date")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="Last update date")
    
    def calculate_total_xp(self) -> int:
        """Calculate total XP from all completed achievements"""
        total = 0
        for achievement in self.achievements:
            if achievement.achieved and achievement.metadata and achievement.metadata.xp_reward:
                total += achievement.metadata.xp_reward
        return total
    
    def get_achievements_by_course(self, course_id: str) -> List[Achievement]:
        """Get all achievements for a specific course"""
        return [a for a in self.achievements if a.course_id == course_id]
    
    def get_recent_achievements(self, limit: int = 5) -> List[Achievement]:
        """Get most recent achievements"""
        completed_achievements = [a for a in self.achievements if a.achieved and a.date_earned]
        return sorted(completed_achievements, key=lambda x: x.date_earned, reverse=True)[:limit]
    
    def get_achievement_stats(self) -> AchievementStats:
        """Calculate achievement statistics"""
        completed_achievements = [a for a in self.achievements if a.achieved]
        
        # Calculate total XP
        total_xp = sum(
            a.metadata.xp_reward if a.metadata and a.metadata.xp_reward else 0 
            for a in completed_achievements
        )
        
        # Calculate average score
        scores = [a.percentage for a in self.achievements if a.percentage is not None]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Count achievements by course
        achievements_by_course = {}
        for achievement in completed_achievements:
            course_id = achievement.course_id
            achievements_by_course[course_id] = achievements_by_course.get(course_id, 0) + 1
        
        # Calculate completion rate
        total_achievements = len(self.achievements)
        completion_rate = (len(completed_achievements) / total_achievements * 100) if total_achievements > 0 else 0
        
        # Find best category
        category_counts = {}
        for achievement in completed_achievements:
            if achievement.metadata and achievement.metadata.category:
                cat = achievement.metadata.category.value
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        best_category = max(category_counts.keys(), key=lambda k: category_counts[k]) if category_counts else None
        
        return AchievementStats(
            total_achievements=len(completed_achievements),
            total_xp=total_xp,
            average_score=round(average_score, 2),
            achievements_by_course=achievements_by_course,
            recent_achievements=self.get_recent_achievements(5),
            completion_rate=round(completion_rate, 2),
            best_category=best_category
        ) 