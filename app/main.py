from fastapi import FastAPI
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
import uvicorn
from app.api.achievements import router as achievements_router

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

@app.get("/")
async def root():
    return {"message": "RavenCode Achievements API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003) 