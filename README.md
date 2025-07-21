# RavenCode Achievements API v2.0.0

🎯 **Enhanced API para gestionar logros de estudiantes en la plataforma RavenCode**

API completamente mejorada con respuestas estandarizadas, validación avanzada, nuevos endpoints, manejo de errores robusto y optimización de base de datos.

---

## 🌟 Nuevas características v2.0.0

- ✅ **Respuestas estandarizadas** con formato consistente
- ✅ **Modelos mejorados** con campos adicionales (XP, metadata, timestamps)
- ✅ **Nuevos endpoints** para estadísticas, eliminación y operaciones masivas
- ✅ **Validación avanzada** con Pydantic validators
- ✅ **Manejo de errores robusto** con excepciones personalizadas
- ✅ **Optimización de base de datos** con índices automáticos
- ✅ **Testing comprehensivo** con script de pruebas automatizado
- ✅ **Documentación OpenAPI mejorada**

---

## 🚀 Inicio rápido

### Opción 1: Script de inicio automático (Recomendado)
```bash
# Clona el repositorio
git clone <repository-url>
cd ravencode-backend-achievements

# Instala dependencias
pip install -r requirements.txt

# Configura las variables de entorno (ver sección configuración)
# Luego ejecuta el script de inicio que incluye inicialización de BD
python startup.py
```

### Opción 2: Inicio manual
```bash
# Activa entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

# Instala dependencias
pip install -r requirements.txt

# Inicializa la base de datos (opcional pero recomendado)
python -m app.DB.initialize

# Inicia el servidor
python -m app.main
```

**🌐 API disponible en:** http://localhost:8003  
**📚 Documentación:** http://localhost:8003/docs  
**🔧 Documentación alternativa:** http://localhost:8003/redoc  
**❤️ Health check:** http://localhost:8003/health

---

## ⚙️ Configuración

Crea un archivo `.env` en la raíz del proyecto:
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ravencode_achievements_db
```

---

## 🧪 Testing

Ejecuta el script de pruebas completo:
```bash
python test_api.py
```

Este script prueba todos los endpoints y funcionalidades de la API v2.0.0.

---

## 📚 API Endpoints

### Respuesta estándar
Todos los endpoints ahora retornan el siguiente formato:
```json
{
  "data": "...",       // Datos de respuesta
  "message": "...",    // Mensaje descriptivo
  "success": true      // Indicador de éxito
}
```

### 🎯 Endpoints principales

#### 1. Actualizar/crear logro
```http
POST /achievements/update
```

**Body:**
```json
{
  "email": "student@example.com",
  "achievement": {
    "achievement_name": "first_lesson_completed",
    "course_id": "python_basics",
    "title": "Primera Lección Completada",
    "description": "Completó la primera lección de Python",
    "metadata": {
      "xp": 50,
      "category": "beginner",
      "difficulty": "easy"
    }
  },
  "score": 85.0,
  "total_points": 100.0
}
```

**Respuesta:**
```json
{
  "data": {
    "email": "student@example.com",
    "achievement": {
      "id": "uuid-here",
      "achievement_name": "first_lesson_completed",
      "course_id": "python_basics",
      "title": "Primera Lección Completada",
      "description": "Completó la primera lección de Python",
      "score": 85.0,
      "total_points": 100.0,
      "percentage": 85.0,
      "date_earned": "2025-01-01T12:00:00",
      "status": "completed",
      "achieved": true,
      "metadata": {
        "xp": 50,
        "category": "beginner",
        "difficulty": "easy"
      }
    },
    "achieved": true,
    "percentage": 85.0,
    "status": "completed"
  },
  "message": "Achievement updated successfully",
  "success": true
}
```

#### 2. Obtener logros de estudiante
```http
GET /achievements/{email}
```

#### 3. Estadísticas de logros
```http
GET /achievements/{email}/stats
```

**Respuesta:**
```json
{
  "data": {
    "total_achievements": 5,
    "completed_achievements": 3,
    "completion_rate": 60.0,
    "total_xp": 250,
    "average_score": 87.5,
    "achievements_by_course": {
      "python_basics": {
        "total": 3,
        "completed": 2,
        "achievements": ["..."]
      }
    },
    "recent_achievements": ["..."]
  },
  "message": "Achievement statistics retrieved successfully",
  "success": true
}
```

#### 4. Logros disponibles por curso
```http
GET /achievements/course/{course_id}/available
```

#### 5. Actualización masiva
```http
POST /achievements/bulk-update
```

**Body:**
```json
{
  "updates": [
    {
      "email": "student1@example.com",
      "achievement": { "..." },
      "score": 90.0,
      "total_points": 100.0
    },
    {
      "email": "student2@example.com",
      "achievement": { "..." },
      "score": 85.0,
      "total_points": 100.0
    }
  ]
}
```

#### 6. Eliminar logro específico
```http
DELETE /achievements/{email}/{achievement_name}
```

---

## 🛡️ Validación y manejo de errores

### Validaciones implementadas:
- ✅ **Email válido** con formato correcto
- ✅ **Score ≤ total_points** no puede ser mayor
- ✅ **Total_points > 0** debe ser positivo
- ✅ **Achievement_name** no puede estar vacío
- ✅ **Cálculo automático** de porcentajes y estado

### Códigos de error:
- `404` - Estudiante o logro no encontrado
- `422` - Datos de entrada inválidos
- `503` - Error de conexión a base de datos
- `400` - Error general de logros
- `500` - Error inesperado del servidor

---

## 🗄️ Optimización de base de datos

### Índices creados automáticamente:
- **email** (único)
- **email + achievement_name** (compuesto)
- **course_id** para logros
- **status** de logros
- **date_earned** (descendente)
- **achieved** status
- **updated_at** (descendente)

---

## 🔄 Migración desde v1.0.0

### Cambios importantes:
1. **Formato de respuesta**: Todas las respuestas ahora usan `StandardResponse`
2. **Campos adicionales**: Los logros tienen más información (score, percentage, metadata, etc.)
3. **Nuevos endpoints**: Estadísticas, eliminación, operaciones masivas

### Compatibilidad:
- ✅ **URLs iguales** para endpoints existentes
- ✅ **Datos existentes** se migran automáticamente
- ⚠️ **Frontend** debe adaptarse al nuevo formato de respuesta

---

## 🧠 Lógica de uso

### 1. **Creación automática de logros**
- Cuando el puntaje ≥ 80% → `achieved: true`, `status: "completed"`
- Cuando 0% < puntaje < 80% → `achieved: false`, `status: "in_progress"`
- Cuando puntaje = 0% → `achieved: false`, `status: "failed"`

### 2. **Cálculos automáticos**
- **Percentage**: `(score / total_points) * 100`
- **Status**: Basado en percentage
- **Date_earned**: Solo cuando `achieved: true`
- **ID único**: UUID generado automáticamente

### 3. **XP y metadata**
- Sistema de **experiencia (XP)** acumulativa
- **Metadata flexible** para categorías, dificultad, etc.
- **Estadísticas** calculadas en tiempo real

---

## 📋 Scripts útiles

```bash
# Iniciar con optimización de BD
python startup.py

# Solo inicializar BD
python -m app.DB.initialize

# Ejecutar tests
python test_api.py

# Verificar conexión a BD
python -c "from app.DB.database import test_connection; test_connection()"
```

---

## 🔧 Desarrollo

### Estructura mejorada:
```
app/
├── main.py              # FastAPI app principal
├── api/
│   └── achievements.py  # Endpoints de logros
├── models/
│   ├── __init__.py     # StandardResponse
│   ├── student.py      # Modelos mejorados
│   └── exceptions.py   # Excepciones personalizadas
├── services/
│   └── achievement_service.py  # Lógica de negocio
└── DB/
    ├── database.py     # Conexión a MongoDB
    └── initialize.py   # Inicialización y índices
```

### Para contribuir:
1. Instala dependencias de desarrollo
2. Ejecuta tests antes de commit
3. Sigue las convenciones de código existentes
4. Actualiza documentación cuando sea necesario

---

## 📞 Soporte

- **Documentación interactiva**: http://localhost:8003/docs
- **Health check**: http://localhost:8003/health
- **Tests**: `python test_api.py`
- **Logs**: Configurados en todos los módulos

---

**🎉 ¡La API v2.0.0 está lista para producción con todas las mejoras recomendadas implementadas!**
