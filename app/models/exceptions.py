from fastapi import HTTPException

class AchievementError(Exception):
    """Base exception for achievement-related errors"""
    pass

class AchievementNotFound(AchievementError):
    """Raised when an achievement is not found"""
    pass

class InvalidAchievementData(AchievementError):
    """Raised when achievement data is invalid"""
    pass

class StudentNotFound(AchievementError):
    """Raised when a student is not found"""
    pass

class DatabaseConnectionError(AchievementError):
    """Raised when database connection fails"""
    pass

class DuplicateAchievementError(AchievementError):
    """Raised when trying to create a duplicate achievement"""
    pass

def create_http_exception_handler(exception_class, status_code: int, default_message: str):
    """Factory function to create HTTP exception handlers"""
    async def handler(request, exc):
        from app.models import StandardResponse
        return HTTPException(
            status_code=status_code,
            detail=StandardResponse.error_response(
                message=str(exc) if str(exc) else default_message
            ).dict()
        )
    return handler 