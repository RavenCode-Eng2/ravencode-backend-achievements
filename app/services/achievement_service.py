from app.DB.database import get_database
from app.models.student import Student, Achievement
from typing import Optional
from pymongo.collection import Collection

# Obtener la colección de estudiantes
_db = get_database()
students_collection: Optional[Collection] = _db["students"] if _db is not None else None

def update_achievement(email: str, achievement_data: dict, score: float, total_points: float) -> dict:
    """
    Actualiza o agrega un logro a un estudiante según el puntaje obtenido.
    Si el puntaje es >= 80% del total, marca el logro como obtenido.
    """
    if students_collection is None:
        return {"error": "No database connection"}

    percent = (score / total_points) * 100 if total_points > 0 else 0
    achieved = percent >= 80

    # Preparar el logro
    achievement = Achievement(**achievement_data, achieved=achieved).dict()

    # Buscar si el estudiante ya existe
    student = students_collection.find_one({"email": email})

    if student:
        # Buscar si ya tiene ese logro
        existing = next((a for a in student.get("achievements", []) if a["achievement_name"] == achievement["achievement_name"]), None)
        if existing:
            # Actualizar el logro existente
            students_collection.update_one(
                {"email": email, "achievements.achievement_name": achievement["achievement_name"]},
                {"$set": {"achievements.$": achievement}}
            )
        else:
            # Agregar el nuevo logro
            students_collection.update_one(
                {"email": email},
                {"$push": {"achievements": achievement}}
            )
    else:
        # Crear el estudiante con el logro
        new_student = Student(email=email, achievements=[Achievement(**achievement)]).dict()
        students_collection.insert_one(new_student)

    return {"email": email, "achievement": achievement, "achieved": achieved, "percent": percent}

def get_student_achievements(email: str) -> Optional[dict]:
    """
    Devuelve los logros de un estudiante por email.
    """
    if students_collection is None:
        return None
    student = students_collection.find_one({"email": email}, {"_id": 0})
    return student 