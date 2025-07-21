from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from app.api.achievements import router as achievements_router, admin_router
from app.api.diplomas import router as diplomas_router
from app.models import StandardResponse
from app.models.exceptions import (
    AchievementError, AchievementNotFound, StudentNotFound,
    InvalidAchievementData, DatabaseConnectionError
)

app = FastAPI(
    title="RavenCode Achievements & Diplomas API",
    description="API para gestionar logros y diplomas de estudiantes en RavenCode Colombia",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(AchievementError)
async def achievement_error_handler(request: Request, exc: AchievementError):
    return JSONResponse(
        status_code=400,
        content=StandardResponse.error_response(message=str(exc)).dict()
    )

@app.exception_handler(AchievementNotFound)
async def achievement_not_found_handler(request: Request, exc: AchievementNotFound):
    return JSONResponse(
        status_code=404,
        content=StandardResponse.error_response(message=str(exc)).dict()
    )

@app.exception_handler(StudentNotFound)
async def student_not_found_handler(request: Request, exc: StudentNotFound):
    return JSONResponse(
        status_code=404,
        content=StandardResponse.error_response(message=str(exc)).dict()
    )

@app.exception_handler(InvalidAchievementData)
async def invalid_achievement_data_handler(request: Request, exc: InvalidAchievementData):
    return JSONResponse(
        status_code=422,
        content=StandardResponse.error_response(message=str(exc)).dict()
    )

@app.exception_handler(DatabaseConnectionError)
async def database_connection_error_handler(request: Request, exc: DatabaseConnectionError):
    return JSONResponse(
        status_code=503,
        content=StandardResponse.error_response(message=str(exc)).dict()
    )

# Include routers
app.include_router(achievements_router)
app.include_router(admin_router)  # Include admin router separately
app.include_router(diplomas_router)

@app.get("/")
async def root():
    return StandardResponse.success_response(
        data={
            "api": "RavenCode Achievements & Diplomas API",
            "version": "2.1.0",
            "status": "running",
            "pais": "Colombia",
            "sistema_notas": "Escala 1.0-5.0",
            "docs_url": "/docs",
            "endpoints": {
                "achievements": "/achievements",
                "admin_achievements": "/admin/achievements",
                "diplomas": "/diplomas",
                "health": "/health"
            }
        },
        message="Bienvenido a RavenCode Achievements & Diplomas API Colombia"
    )

@app.get("/health")
async def health_check():
    return StandardResponse.success_response(
        data={
            "status": "healthy",
            "version": "2.1.0",
            "sistema": "Colombia",
            "timestamp": "2024-01-01T00:00:00Z"
        },
        message="Servicio funcionando correctamente"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003) 