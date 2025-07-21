from app.DB.database import get_database
from app.models.diploma import (
    Diploma, PlantillaDiploma, RequisitosDiploma, 
    VerificacionElegibilidadDiploma, SolicitudDiploma,
    ConfiguracionDiplomasColombia
)
from app.models.student import Student, Achievement
from app.models.exceptions import (
    DatabaseConnectionError, StudentNotFound, AchievementNotFound,
    InvalidAchievementData
)
from app.services.achievement_service import get_student_achievements
from typing import Optional, List, Dict, Any
from pymongo.collection import Collection
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

# Obtener las colecciones
_db = get_database()
students_collection: Optional[Collection] = _db["students"] if _db is not None else None
diplomas_collection: Optional[Collection] = _db["diplomas"] if _db is not None else None
plantillas_diplomas_collection: Optional[Collection] = _db["plantillas_diplomas"] if _db is not None else None

def _verificar_conexion_bd():
    """Verificar si la conexión a la base de datos está disponible"""
    if students_collection is None or diplomas_collection is None:
        raise DatabaseConnectionError("No hay conexión disponible a la base de datos")

def convertir_porcentaje_a_nota_colombiana(porcentaje: float) -> float:
    """
    Convertir porcentaje (0-100) a nota colombiana (1.0-5.0)
    
    Mapeo estándar:
    - 95-100% = 4.6-5.0 (Excelente)
    - 85-94% = 4.0-4.5 (Sobresaliente) 
    - 75-84% = 3.5-3.9 (Bueno)
    - 65-74% = 3.0-3.4 (Aceptable)
    - 55-64% = 2.0-2.9 (Insuficiente)
    - <55% = 1.0-1.9 (Deficiente)
    """
    if porcentaje >= 95:
        return round(4.6 + (porcentaje - 95) * 0.08, 1)  # 4.6-5.0
    elif porcentaje >= 85:
        return round(4.0 + (porcentaje - 85) * 0.05, 1)  # 4.0-4.5
    elif porcentaje >= 75:
        return round(3.5 + (porcentaje - 75) * 0.04, 1)  # 3.5-3.9
    elif porcentaje >= 65:
        return round(3.0 + (porcentaje - 65) * 0.04, 1)  # 3.0-3.4
    elif porcentaje >= 55:
        return round(2.0 + (porcentaje - 55) * 0.09, 1)  # 2.0-2.9
    else:
        return round(1.0 + porcentaje * 0.018, 1)  # 1.0-1.9

def crear_plantilla_diploma(plantilla_data: dict) -> dict:
    """Crear una nueva plantilla de diploma"""
    _verificar_conexion_bd()
    
    plantilla = PlantillaDiploma(**plantilla_data)
    plantilla_dict = plantilla.dict()
    plantilla_dict["id"] = str(uuid.uuid4())
    plantilla_dict["fecha_creacion"] = datetime.now()
    
    # Insertar en la base de datos
    result = plantillas_diplomas_collection.insert_one(plantilla_dict)
    plantilla_dict["_id"] = str(result.inserted_id)
    
    logger.info(f"Plantilla de diploma creada: {plantilla.nombre_diploma}")
    return plantilla_dict

def obtener_plantilla_diploma(id_curso: str, tipo_diploma: str) -> Optional[PlantillaDiploma]:
    """Obtener plantilla de diploma por curso y tipo"""
    _verificar_conexion_bd()
    
    plantilla_doc = plantillas_diplomas_collection.find_one({
        "id_curso": id_curso,
        "tipo_diploma": tipo_diploma
    })
    
    if not plantilla_doc:
        return None
    
    plantilla_doc.pop("_id", None)
    return PlantillaDiploma(**plantilla_doc)

def verificar_elegibilidad_diploma(email: str, id_curso: str, tipo_diploma: str) -> VerificacionElegibilidadDiploma:
    """Verificar si un estudiante es elegible para un diploma"""
    _verificar_conexion_bd()
    
    try:
        # Obtener logros del estudiante
        estudiante_data = get_student_achievements(email)
        estudiante = Student(**estudiante_data)
        
        # Obtener plantilla del diploma
        plantilla = obtener_plantilla_diploma(id_curso, tipo_diploma)
        if not plantilla:
            return VerificacionElegibilidadDiploma(
                elegible=False,
                mensaje=f"No se encontró plantilla para diploma tipo '{tipo_diploma}' del curso '{id_curso}'",
                observaciones="Contacte al administrador para crear la plantilla de diploma"
            )
        
        # Verificar cada requisito
        requisitos_completados = []
        requisitos_faltantes = []
        notas_requisitos = []
        horas_completadas = 0
        
        logros_estudiante = {logro.achievement_name: logro for logro in estudiante.achievements if logro.course_id == id_curso}
        
        for requisito in plantilla.requisitos:
            logro = logros_estudiante.get(requisito.nombre_logro)
            
            if logro and logro.achieved:
                # Convertir porcentaje a nota colombiana
                nota_colombiana = convertir_porcentaje_a_nota_colombiana(logro.percentage or 0)
                
                requisito_completado = {
                    "nombre_logro": requisito.nombre_logro,
                    "nota_obtenida": nota_colombiana,
                    "nota_minima": requisito.nota_minima,
                    "cumple_requisito": nota_colombiana >= requisito.nota_minima,
                    "fecha_completado": logro.date_earned,
                    "porcentaje_original": logro.percentage
                }
                
                if nota_colombiana >= requisito.nota_minima:
                    requisitos_completados.append(requisito_completado)
                    notas_requisitos.append(nota_colombiana)
                    # Simular horas completadas (esto debería venir de los metadatos del logro)
                    horas_completadas += logro.metadata.get('horas', 10) if logro.metadata else 10
                else:
                    requisitos_faltantes.append(requisito)
            else:
                if requisito.es_obligatorio:
                    requisitos_faltantes.append(requisito)
        
        # Calcular estadísticas
        total_requisitos = len(plantilla.requisitos)
        requisitos_cumplidos = len(requisitos_completados)
        porcentaje_completado = (requisitos_cumplidos / total_requisitos) * 100 if total_requisitos > 0 else 0
        nota_promedio = sum(notas_requisitos) / len(notas_requisitos) if notas_requisitos else 0
        
        # Determinar elegibilidad
        requisitos_obligatorios_faltantes = [r for r in requisitos_faltantes if r.es_obligatorio]
        elegible = len(requisitos_obligatorios_faltantes) == 0 and nota_promedio >= ConfiguracionDiplomasColombia.NOTA_MINIMA_APROBACION
        
        # Crear mensaje
        if elegible:
            mensaje = f"¡Felicidades! Cumples todos los requisitos para el diploma '{plantilla.nombre_diploma}'"
            observaciones = f"Nota promedio: {nota_promedio:.1f} - {ConfiguracionDiplomasColombia.obtener_calificacion_cualitativa(nota_promedio)}"
        else:
            mensaje = f"Aún no cumples todos los requisitos para el diploma '{plantilla.nombre_diploma}'"
            if nota_promedio < ConfiguracionDiplomasColombia.NOTA_MINIMA_APROBACION:
                observaciones = f"Nota promedio insuficiente: {nota_promedio:.1f} (mínimo requerido: {ConfiguracionDiplomasColombia.NOTA_MINIMA_APROBACION})"
            else:
                observaciones = f"Faltan {len(requisitos_obligatorios_faltantes)} requisitos obligatorios"
        
        return VerificacionElegibilidadDiploma(
            elegible=elegible,
            plantilla_diploma=plantilla,
            requisitos_completados=requisitos_completados,
            requisitos_faltantes=requisitos_faltantes,
            nota_promedio=nota_promedio,
            horas_completadas=horas_completadas,
            porcentaje_completado=porcentaje_completado,
            mensaje=mensaje,
            observaciones=observaciones
        )
        
    except StudentNotFound:
        return VerificacionElegibilidadDiploma(
            elegible=False,
            mensaje="Estudiante no encontrado",
            observaciones="Verifica que el email sea correcto y que el estudiante tenga logros registrados"
        )
    except Exception as e:
        logger.error(f"Error verificando elegibilidad: {e}")
        return VerificacionElegibilidadDiploma(
            elegible=False,
            mensaje="Error interno al verificar elegibilidad",
            observaciones=f"Error técnico: {str(e)}"
        )

def generar_diploma(solicitud: SolicitudDiploma) -> dict:
    """Generar un diploma para un estudiante"""
    _verificar_conexion_bd()
    
    # Verificar elegibilidad
    elegibilidad = verificar_elegibilidad_diploma(
        solicitud.email, 
        solicitud.id_curso, 
        solicitud.tipo_diploma
    )
    
    if not elegibilidad.elegible and not solicitud.forzar_generacion:
        return {
            "exito": False,
            "mensaje": "No cumple los requisitos para el diploma",
            "elegibilidad": elegibilidad.dict()
        }
    
    # Verificar si ya existe un diploma para este estudiante y curso
    diploma_existente = diplomas_collection.find_one({
        "email": solicitud.email,
        "id_curso": solicitud.id_curso,
        "tipo_diploma": solicitud.tipo_diploma
    })
    
    if diploma_existente:
        return {
            "exito": False,
            "mensaje": "Ya existe un diploma para este estudiante y curso",
            "diploma_existente": str(diploma_existente.get("id"))
        }
    
    # Crear el diploma
    plantilla = elegibilidad.plantilla_diploma
    fecha_actual = datetime.now()
    
    # Calcular fecha de vencimiento si aplica
    fecha_vencimiento = None
    if plantilla and hasattr(plantilla, 'meses_vencimiento') and plantilla.meses_vencimiento:
        fecha_vencimiento = fecha_actual + timedelta(days=plantilla.meses_vencimiento * 30)
    
    diploma_data = {
        "id": str(uuid.uuid4()),
        "email": solicitud.email,
        "tipo_diploma": solicitud.tipo_diploma,
        "id_curso": solicitud.id_curso,
        "nombre_diploma": plantilla.nombre_diploma if plantilla else f"Diploma de {solicitud.tipo_diploma}",
        "titulo_diploma": plantilla.titulo_diploma if plantilla else f"Certificado de Finalización",
        "institucion_emisora": plantilla.institucion_emisora if plantilla else "RavenCode Colombia",
        "fecha_obtencion": fecha_actual,
        "fecha_expedicion": fecha_actual,
        "fecha_vencimiento": fecha_vencimiento,
        "codigo_verificacion": f"RC-{uuid.uuid4().hex[:8].upper()}",
        "creditos_academicos": plantilla.creditos_academicos if plantilla else None,
        "horas_academicas": elegibilidad.horas_completadas or (plantilla.horas_academicas if plantilla else None),
        "nota_final": elegibilidad.nota_promedio,
        "calificacion_cualitativa": ConfiguracionDiplomasColombia.obtener_calificacion_cualitativa(elegibilidad.nota_promedio) if elegibilidad.nota_promedio else None,
        "promedio_ponderado": elegibilidad.nota_promedio,
        "modalidad": plantilla.modalidad if plantilla else "Virtual",
        "nivel_educativo": plantilla.nivel_educativo if plantilla else "Educación Continua",
        "codigo_snies": plantilla.codigo_snies if plantilla else None,
        "requisitos_completados": elegibilidad.requisitos_completados,
        "metadata": {
            "idioma": solicitud.idioma,
            "formato_entrega": solicitud.formato_entrega,
            "incluir_apostilla": solicitud.incluir_apostilla,
            "porcentaje_completado": elegibilidad.porcentaje_completado,
            "forzar_generacion": solicitud.forzar_generacion
        }
    }
    
    # Insertar en la base de datos
    diploma = Diploma(**diploma_data)
    result = diplomas_collection.insert_one(diploma.dict())
    
    logger.info(f"Diploma generado para {solicitud.email}: {diploma.nombre_diploma}")
    
    return {
        "exito": True,
        "mensaje": "Diploma generado exitosamente",
        "diploma": diploma.dict(),
        "codigo_verificacion": diploma.codigo_verificacion,
        "elegibilidad": elegibilidad.dict()
    }

def obtener_diplomas_estudiante(email: str) -> List[Dict[str, Any]]:
    """Obtener todos los diplomas de un estudiante"""
    _verificar_conexion_bd()
    
    diplomas = list(diplomas_collection.find({"email": email}, {"_id": 0}))
    
    # Agregar información de estado
    for diploma in diplomas:
        diploma_obj = Diploma(**diploma)
        diploma["esta_vencido"] = diploma_obj.esta_vencido()
        diploma["equivalencia_internacional"] = diploma_obj.obtener_equivalencia_internacional()
    
    return diplomas

def verificar_diploma(codigo_verificacion: str) -> Optional[Dict[str, Any]]:
    """Verificar la autenticidad de un diploma por código de verificación"""
    _verificar_conexion_bd()
    
    diploma = diplomas_collection.find_one({"codigo_verificacion": codigo_verificacion}, {"_id": 0})
    
    if not diploma:
        return None
    
    diploma_obj = Diploma(**diploma)
    
    return {
        "valido": True,
        "diploma": diploma,
        "esta_vencido": diploma_obj.esta_vencido(),
        "mensaje": "Diploma válido" if not diploma_obj.esta_vencido() else "Diploma válido pero vencido"
    }

def obtener_estadisticas_diplomas() -> Dict[str, Any]:
    """Obtener estadísticas generales de diplomas"""
    _verificar_conexion_bd()
    
    pipeline = [
        {
            "$group": {
                "_id": "$tipo_diploma",
                "total": {"$sum": 1},
                "promedio_notas": {"$avg": "$nota_final"},
                "diplomas_recientes": {
                    "$sum": {
                        "$cond": [
                            {"$gte": ["$fecha_obtencion", datetime.now() - timedelta(days=30)]},
                            1,
                            0
                        ]
                    }
                }
            }
        }
    ]
    
    stats_por_tipo = list(diplomas_collection.aggregate(pipeline))
    
    total_diplomas = diplomas_collection.count_documents({})
    diplomas_vigentes = diplomas_collection.count_documents({
        "$or": [
            {"fecha_vencimiento": None},
            {"fecha_vencimiento": {"$gt": datetime.now()}}
        ]
    })
    
    return {
        "total_diplomas": total_diplomas,
        "diplomas_vigentes": diplomas_vigentes,
        "diplomas_vencidos": total_diplomas - diplomas_vigentes,
        "estadisticas_por_tipo": stats_por_tipo,
        "configuracion_colombia": {
            "escala_notas": f"{ConfiguracionDiplomasColombia.ESCALA_NUMERICA_MIN}-{ConfiguracionDiplomasColombia.ESCALA_NUMERICA_MAX}",
            "nota_minima_aprobacion": ConfiguracionDiplomasColombia.NOTA_MINIMA_APROBACION,
            "tipos_diploma_disponibles": ConfiguracionDiplomasColombia.TIPOS_DIPLOMA
        }
    }

def eliminar_diploma(email: str, diploma_id: str) -> bool:
    """Eliminar un diploma específico"""
    _verificar_conexion_bd()
    
    result = diplomas_collection.delete_one({
        "id": diploma_id,
        "email": email
    })
    
    if result.deleted_count > 0:
        logger.info(f"Diploma eliminado: {diploma_id} para {email}")
        return True
    
    return False 