# RavenCode Achievements API

API para gestionar los logros de estudiantes en la plataforma RavenCode. Permite registrar, actualizar y consultar logros asociados a estudiantes según su desempeño en módulos/cursos.

---

## 🚀 ¿Cómo levantar el backend?

### 1. Clona el repositorio y entra a la carpeta
```bash
cd ravencode-backend-achievements
```

### 2. Crea y activa un entorno virtual (recomendado)
```bash
python -m venv venv
# En Windows:
.\venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 3. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 4. Configura las variables de entorno
Crea un archivo `.env` en la raíz del proyecto con la cadena de conexión a MongoDB:
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ravencode_achievements_db
```
Ajusta los valores según tu entorno.

### 5. Levanta el servidor
```bash
uvicorn app.main:app --reload --port 8003
```

La API estará disponible en: [http://localhost:8003](http://localhost:8003)

Puedes ver la documentación interactiva en: [http://localhost:8003/docs](http://localhost:8003/docs)

---

## 🧠 Lógica de uso e integración desde el frontend

### 1. Registrar/actualizar un logro para un estudiante

**Endpoint:**
```
POST /achievements/update
```

**Body esperado:**
```json
{
  "email": "juan.perez@example.com",
  "achievement": {
    "achievement_name": "logro_001",
    "course_id": "curso_python",
    "title": "Curso de Python completado",
    "description": "Completó el curso básico de Python"
  },
  "score": 85,
  "total_points": 100
}
```

- Si el estudiante obtiene **80% o más** (`score/total_points >= 0.8`), el logro se marca como obtenido (`achieved: true`).
- Si no, se marca como no obtenido (`achieved: false`).
- Si el estudiante no existe, se crea automáticamente.
- Si el logro ya existe, se actualiza.

**Respuesta:**
```json
{
  "email": "juan.perez@example.com",
  "achievement": {
    "achievement_name": "logro_001",
    "course_id": "curso_python",
    "title": "Curso de Python completado",
    "description": "Completó el curso básico de Python",
    "achieved": true
  },
  "achieved": true,
  "percent": 85.0
}
```

### 2. Consultar los logros de un estudiante

**Endpoint:**
```
GET /achievements/{email}
```

**Respuesta ejemplo:**
```json
{
  "email": "juan.perez@example.com",
  "achievements": [
    {
      "achievement_name": "logro_001",
      "course_id": "curso_python",
      "title": "Curso de Python completado",
      "description": "Completó el curso básico de Python",
      "achieved": true
    },
    ...
  ]
}
```

---

## 🧪 Lógica para testear desde el frontend

1. **Registrar un logro:**
   - Envía un POST a `/achievements/update` con los datos del estudiante, logro, puntaje obtenido y puntaje total.
   - Verifica que la respuesta incluya el campo `achieved` correctamente calculado.

2. **Consultar logros:**
   - Haz un GET a `/achievements/{email}` y verifica que los logros estén correctamente almacenados y el campo `achieved` refleje el estado real.

3. **Casos de prueba sugeridos:**
   - Puntaje menor al 80%: el logro debe estar con `achieved: false`.
   - Puntaje igual o mayor al 80%: el logro debe estar con `achieved: true`.
   - Actualizar un logro existente: debe sobrescribir el estado anterior.
   - Consultar un estudiante inexistente: debe devolver error 404.

---

## 📦 Notas adicionales
- Puedes usar herramientas como Postman, Thunder Client o fetch/axios desde el frontend para probar los endpoints.
- La API está lista para integrarse con React, Vue, Angular, etc.
- Recuerda proteger los endpoints en producción (autenticación, CORS, etc.).
