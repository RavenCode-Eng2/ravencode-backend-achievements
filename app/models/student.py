from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class Achievement(BaseModel):
    achievement_name: str = Field(..., description="nombre único del logro")
    course_id: str = Field(..., description="ID del curso asociado")
    title: str
    description: Optional[str] = None
    achieved: bool = Field(False, description="Indica si el logro ya fue obtenido por el estudiante")

class Student(BaseModel):
    email: EmailStr = Field(..., description="Correo del estudiante")
    achievements: List[Achievement] = [] 