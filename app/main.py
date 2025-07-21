from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
from app.api.achievements import router as achievements_router
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.core.metrics import REQUEST_COUNT, RESPONSE_TIME, ERROR_COUNT

app = FastAPI(
    title="RavenCode Achievements API",
    description="API para gestionar logros de estudiantes en RavenCode",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(achievements_router)

# Middleware para registrar métricas
@app.middleware("http")
async def record_metrics(request, call_next):
    method = request.method
    endpoint = request.url.path

    # Registrar la hora de inicio para medir el tiempo de respuesta
    start_time = time.time()

    # Continuar con la solicitud
    response = await call_next(request)

    # Medir tiempo de respuesta
    duration = time.time() - start_time
    RESPONSE_TIME.labels(method=method, endpoint=endpoint).observe(duration)

    # Incrementar contador de peticiones
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()

    # Si hay un error (código de estado >= 400), aumentar el contador de errores
    if response.status_code >= 400:
        ERROR_COUNT.labels(method=method, endpoint=endpoint).inc()

    return response

# Ruta para exponer las métricas en formato Prometheus
@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    return {"message": "RavenCode Achievements API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003) from fastapi import FastAPI
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