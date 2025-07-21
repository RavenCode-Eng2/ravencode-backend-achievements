from typing import Any, Optional
from pydantic import BaseModel

class StandardResponse(BaseModel):
    """Standard API response format"""
    data: Optional[Any] = None
    message: str = "Success"
    success: bool = True
    
    @classmethod
    def success_response(cls, data: Any = None, message: str = "Success"):
        return cls(data=data, message=message, success=True)
    
    @classmethod
    def error_response(cls, message: str = "Error", data: Any = None):
        return cls(data=data, message=message, success=False) 