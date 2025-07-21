from fastapi import APIRouter, HTTPException, Query
from pydantic import EmailStr
from typing import Optional, List, Dict, Any
from app.services.diploma_service import (
    verificar_elegibilidad_diploma, generar_diploma, obtener_diplomas_estudiante,
    verificar_diploma, crear_plantilla_diploma, obtener_estadisticas_diplomas,
    eliminar_diploma
)
from app.models.diploma import (
    SolicitudDiploma, PlantillaDiploma, VerificacionElegibilidadDiploma,
    ConfiguracionDiplomasColombia
)
from app.models import StandardResponse
from app.models.exceptions import (
    AchievementError, StudentNotFound, DatabaseConnectionError
)

router = APIRouter(prefix="/diplomas", tags=["Diplomas Colombia"])

@router.get(
    "/configuracion",
    summary="Obtener configuración del sistema de diplomas colombiano",
    description="Recupera la configuración específica para diplomas en Colombia",
    response_description="Configuración del sistema educativo colombiano"
)
async def obtener_configuracion_colombia():
    try:
        config = {
            "escala_notas": {
                "minima": ConfiguracionDiplomasColombia.ESCALA_NUMERICA_MIN,
                "maxima": ConfiguracionDiplomasColombia.ESCALA_NUMERICA_MAX,
                "aprobacion": ConfiguracionDiplomasColombia.NOTA_MINIMA_APROBACION
            },
            "tipos_diploma": ConfiguracionDiplomasColombia.TIPOS_DIPLOMA,
            "niveles_educativos": ConfiguracionDiplomasColombia.NIVELES_EDUCATIVOS,
            "modalidades": ConfiguracionDiplomasColombia.MODALIDADES,
            "calificaciones_cualitativas": ConfiguracionDiplomasColombia.CALIFICACIONES_CUALITATIVAS,
            "ejemplos_conversion": {
                "100%": "5.0 (Excelente)",
                "95%": "4.6 (Excelente)", 
                "85%": "4.0 (Sobresaliente)",
                "75%": "3.5 (Bueno)",
                "65%": "3.0 (Aceptable)",
                "55%": "2.0 (Insuficiente)"
            }
        }
        
        return StandardResponse.success_response(
            data=config,
            message="Configuración del sistema de diplomas colombiano"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=StandardResponse.error_response(message=f"Error obteniendo configuración: {str(e)}").dict()
        )

@router.get(
    "/verificar-elegibilidad/{email}",
    summary="Verificar elegibilidad para diploma",
    description="Verifica si un estudiante cumple los requisitos para obtener un diploma específico",
    response_description="Estado de elegibilidad del estudiante"
)
async def verificar_elegibilidad_endpoint(
    email: EmailStr,
    id_curso: str = Query(..., description="ID del curso"),
    tipo_diploma: str = Query("curso", description="Tipo de diploma a verificar")
):
    try:
        elegibilidad = verificar_elegibilidad_diploma(email, id_curso, tipo_diploma)
        
        return StandardResponse.success_response(
            data=elegibilidad.dict(),
            message="Verificación de elegibilidad completada"
        )
    except StudentNotFound as e:
        raise HTTPException(
            status_code=404,
            detail=StandardResponse.error_response(message=str(e)).dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=StandardResponse.error_response(message=f"Error verificando elegibilidad: {str(e)}").dict()
        )

@router.post(
    "/generar",
    summary="Generar diploma colombiano",
    description="Genera un diploma para un estudiante que cumple los requisitos",
    response_description="Resultado de la generación del diploma"
)
async def generar_diploma_endpoint(solicitud: SolicitudDiploma):
    try:
        resultado = generar_diploma(solicitud)
        
        if resultado["exito"]:
            return StandardResponse.success_response(
                data=resultado,
                message="Diploma generado exitosamente"
            )
        else:
            return StandardResponse.error_response(
                message=resultado["mensaje"],
                data=resultado
            )
    except AchievementError as e:
        raise HTTPException(
            status_code=400,
            detail=StandardResponse.error_response(message=str(e)).dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=StandardResponse.error_response(message=f"Error generando diploma: {str(e)}").dict()
        )

@router.get(
    "/estudiante/{email}",
    summary="Obtener diplomas de un estudiante",
    description="Recupera todos los diplomas obtenidos por un estudiante específico",
    response_description="Lista de diplomas del estudiante"
)
async def obtener_diplomas_estudiante_endpoint(email: EmailStr):
    try:
        diplomas = obtener_diplomas_estudiante(email)
        
        return StandardResponse.success_response(
            data={
                "email": email,
                "total_diplomas": len(diplomas),
                "diplomas": diplomas
            },
            message=f"Diplomas del estudiante {email} recuperados exitosamente"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=StandardResponse.error_response(message=f"Error obteniendo diplomas: {str(e)}").dict()
        )

@router.get(
    "/verificar/{codigo_verificacion}",
    summary="Verificar autenticidad de diploma",
    description="Verifica la autenticidad de un diploma mediante su código de verificación",
    response_description="Estado de verificación del diploma"
)
async def verificar_diploma_endpoint(codigo_verificacion: str):
    try:
        resultado = verificar_diploma(codigo_verificacion)
        
        if resultado:
            return StandardResponse.success_response(
                data=resultado,
                message="Diploma verificado exitosamente"
            )
        else:
            return StandardResponse.error_response(
                message="Código de verificación no válido",
                data={"codigo_verificacion": codigo_verificacion, "valido": False}
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=StandardResponse.error_response(message=f"Error verificando diploma: {str(e)}").dict()
        )

@router.post(
    "/plantillas",
    summary="Crear plantilla de diploma",
    description="Crea una nueva plantilla de diploma para un curso específico",
    response_description="Plantilla de diploma creada"
)
async def crear_plantilla_endpoint(plantilla: PlantillaDiploma):
    try:
        resultado = crear_plantilla_diploma(plantilla.dict())
        
        return StandardResponse.success_response(
            data=resultado,
            message=f"Plantilla de diploma '{plantilla.nombre_diploma}' creada exitosamente"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=StandardResponse.error_response(message=f"Error creando plantilla: {str(e)}").dict()
        )

@router.get(
    "/estadisticas",
    summary="Obtener estadísticas de diplomas",
    description="Recupera estadísticas generales del sistema de diplomas",
    response_description="Estadísticas del sistema de diplomas"
)
async def obtener_estadisticas_endpoint():
    try:
        estadisticas = obtener_estadisticas_diplomas()
        
        return StandardResponse.success_response(
            data=estadisticas,
            message="Estadísticas de diplomas recuperadas exitosamente"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=StandardResponse.error_response(message=f"Error obteniendo estadísticas: {str(e)}").dict()
        )

@router.delete(
    "/estudiante/{email}/{diploma_id}",
    summary="Eliminar diploma específico",
    description="Elimina un diploma específico de un estudiante",
    response_description="Resultado de la eliminación"
)
async def eliminar_diploma_endpoint(email: EmailStr, diploma_id: str):
    try:
        eliminado = eliminar_diploma(email, diploma_id)
        
        if eliminado:
            return StandardResponse.success_response(
                data={"diploma_id": diploma_id, "eliminado": True},
                message="Diploma eliminado exitosamente"
            )
        else:
            return StandardResponse.error_response(
                message="Diploma no encontrado o no se pudo eliminar",
                data={"diploma_id": diploma_id, "eliminado": False}
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=StandardResponse.error_response(message=f"Error eliminando diploma: {str(e)}").dict()
        )

@router.get(
    "/convertir-nota",
    summary="Convertir porcentaje a nota colombiana",
    description="Convierte un porcentaje (0-100) a la escala de notas colombiana (1.0-5.0)",
    response_description="Conversión de nota"
)
async def convertir_nota_endpoint(porcentaje: float = Query(..., ge=0, le=100, description="Porcentaje a convertir")):
    try:
        from app.services.diploma_service import convertir_porcentaje_a_nota_colombiana
        
        nota_colombiana = convertir_porcentaje_a_nota_colombiana(porcentaje)
        calificacion_cualitativa = ConfiguracionDiplomasColombia.obtener_calificacion_cualitativa(nota_colombiana)
        
        # Calcular equivalencia internacional
        if nota_colombiana >= 4.6:
            equivalencia = "A+ (95-100%)"
        elif nota_colombiana >= 4.0:
            equivalencia = "A (85-94%)"
        elif nota_colombiana >= 3.5:
            equivalencia = "B+ (75-84%)"
        elif nota_colombiana >= 3.0:
            equivalencia = "B (65-74%)"
        elif nota_colombiana >= 2.0:
            equivalencia = "C (55-64%)"
        else:
            equivalencia = "F (<55%)"
        
        resultado = {
            "porcentaje_original": porcentaje,
            "nota_colombiana": nota_colombiana,
            "calificacion_cualitativa": calificacion_cualitativa,
            "equivalencia_internacional": equivalencia,
            "aprobado": nota_colombiana >= ConfiguracionDiplomasColombia.NOTA_MINIMA_APROBACION
        }
        
        return StandardResponse.success_response(
            data=resultado,
            message="Conversión de nota completada"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=StandardResponse.error_response(message=f"Error convirtiendo nota: {str(e)}").dict()
        ) 