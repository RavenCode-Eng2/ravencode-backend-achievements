from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.services.achievement_service import update_achievement, get_student_achievements

router = APIRouter(prefix="/achievements", tags=["Achievements"])

class AchievementInput(BaseModel):
    achievement_name: str = Field(..., description="nombre único del logro")
    course_id: str = Field(..., description="ID del curso asociado")
    title: str
    description: Optional[str] = None

class AchievementUpdateRequest(BaseModel):
    email: EmailStr
    achievement: AchievementInput
    score: float = Field(..., description="Puntaje obtenido por el estudiante")
    total_points: float = Field(..., description="Puntaje total posible")

@router.post("/update", summary="Actualizar/agregar logro de estudiante")
def update_student_achievement(request: AchievementUpdateRequest):
    result = update_achievement(
        email=request.email,
        achievement_data=request.achievement.dict(),
        score=request.score,
        total_points=request.total_points
    )
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.get("/{email}", summary="Obtener logros de un estudiante")
def get_achievements(email: EmailStr):
    student = get_student_achievements(email)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return student 