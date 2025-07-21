from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any, ClassVar
from datetime import datetime
from app.models.student import Achievement

class RequisitosDiploma(BaseModel):
    """Representa un requisito para obtener un diploma colombiano"""
    nombre_logro: str = Field(..., description="Nombre del logro requerido")
    id_curso: str = Field(..., description="ID del curso para el requisito")
    nota_minima: Optional[float] = Field(3.0, ge=1.0, le=5.0, description="Nota mínima requerida (escala 1.0-5.0)")
    es_obligatorio: bool = Field(True, description="Si este requisito es obligatorio")

class PlantillaDiploma(BaseModel):
    """Plantilla de configuración para diplomas colombianos"""
    tipo_diploma: str = Field(..., description="Tipo de diploma (curso, diplomado, certificacion, especializacion)")
    id_curso: str = Field(..., description="ID del curso para este diploma")
    nombre_diploma: str = Field(..., description="Nombre oficial del diploma")
    titulo_diploma: str = Field(..., description="Título mostrado en el diploma")
    descripcion: Optional[str] = Field(None, description="Descripción del diploma")
    institucion_emisora: str = Field("RavenCode Colombia", description="Institución que emite el diploma")
    requisitos: List[RequisitosDiploma] = Field(..., description="Lista de requisitos para obtener este diploma")
    url_plantilla: Optional[str] = Field(None, description="URL del diseño de la plantilla")
    creditos_academicos: Optional[int] = Field(None, ge=0, description="Créditos académicos otorgados")
    horas_academicas: Optional[int] = Field(None, ge=0, description="Horas académicas del programa")
    modalidad: str = Field("Virtual", description="Modalidad del programa (Presencial, Virtual, Mixta)")
    nivel_educativo: str = Field("Educación Continua", description="Nivel educativo (Técnico, Tecnológico, Profesional, Especialización)")
    codigo_snies: Optional[str] = Field(None, description="Código SNIES si aplica")
    
    @validator('requisitos')
    def validar_requisitos_no_vacios(cls, v):
        if not v:
            raise ValueError('El diploma debe tener al menos un requisito')
        return v
    
    @validator('tipo_diploma')
    def validar_tipo_diploma(cls, v):
        tipos_validos = ['curso', 'diplomado', 'certificacion', 'especializacion', 'tecnico', 'tecnologico']
        if v.lower() not in tipos_validos:
            raise ValueError(f'Tipo de diploma debe ser uno de: {tipos_validos}')
        return v.lower()

class Diploma(BaseModel):
    """Representa un diploma colombiano obtenido"""
    id: Optional[str] = None
    email: EmailStr = Field(..., description="Email del estudiante")
    tipo_diploma: str = Field(..., description="Tipo de diploma")
    id_curso: str = Field(..., description="ID del curso")
    nombre_diploma: str = Field(..., description="Nombre oficial del diploma")
    titulo_diploma: str = Field(..., description="Título en el diploma")
    institucion_emisora: str = Field("RavenCode Colombia", description="Institución emisora")
    fecha_obtencion: datetime = Field(default_factory=datetime.now, description="Fecha de obtención del diploma")
    fecha_expedicion: Optional[datetime] = Field(None, description="Fecha de expedición del certificado")
    fecha_vencimiento: Optional[datetime] = Field(None, description="Fecha de vencimiento (si aplica)")
    url_certificado: Optional[str] = Field(None, description="URL del certificado generado")
    codigo_verificacion: Optional[str] = Field(None, description="Código único de verificación")
    creditos_academicos: Optional[int] = Field(None, ge=0, description="Créditos académicos otorgados")
    horas_academicas: Optional[int] = Field(None, ge=0, description="Horas académicas completadas")
    nota_final: Optional[float] = Field(None, ge=1.0, le=5.0, description="Nota final (escala 1.0-5.0)")
    calificacion_cualitativa: Optional[str] = Field(None, description="Calificación cualitativa")
    promedio_ponderado: Optional[float] = Field(None, ge=1.0, le=5.0, description="Promedio ponderado final")
    modalidad: str = Field("Virtual", description="Modalidad del programa")
    nivel_educativo: str = Field("Educación Continua", description="Nivel educativo")
    registro_calificado: Optional[str] = Field(None, description="Número de registro calificado")
    codigo_snies: Optional[str] = Field(None, description="Código SNIES")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadatos adicionales del diploma")
    
    # Requisitos completados para obtener este diploma
    requisitos_completados: List[Dict[str, Any]] = Field(default_factory=list, description="Requisitos completados")
    
    def esta_vencido(self) -> bool:
        """Verificar si el diploma ha vencido"""
        if self.fecha_vencimiento is None:
            return False
        return datetime.now() > self.fecha_vencimiento
    
    def obtener_calificacion_cualitativa(self) -> str:
        """Calcular calificación cualitativa colombiana desde la nota numérica"""
        if self.nota_final is None:
            return "No Aplica"
        
        nota = self.nota_final
        if nota >= 4.6:
            return "Excelente"
        elif nota >= 4.0:
            return "Sobresaliente"
        elif nota >= 3.5:
            return "Bueno"
        elif nota >= 3.0:
            return "Aceptable"
        elif nota >= 2.0:
            return "Insuficiente"
        else:
            return "Deficiente"
    
    def obtener_equivalencia_internacional(self) -> str:
        """Obtener equivalencia internacional de la nota colombiana"""
        if self.nota_final is None:
            return "N/A"
        
        nota = self.nota_final
        if nota >= 4.6:
            return "A+ (95-100%)"
        elif nota >= 4.0:
            return "A (85-94%)"
        elif nota >= 3.5:
            return "B+ (75-84%)"
        elif nota >= 3.0:
            return "B (65-74%)"
        elif nota >= 2.0:
            return "C (55-64%)"
        else:
            return "F (<55%)"

class VerificacionElegibilidadDiploma(BaseModel):
    """Resultado de verificar si el estudiante es elegible para un diploma"""
    elegible: bool = Field(..., description="Si el estudiante es elegible")
    plantilla_diploma: Optional[PlantillaDiploma] = Field(None, description="Plantilla del diploma si es elegible")
    requisitos_completados: List[Dict[str, Any]] = Field(default_factory=list, description="Requisitos cumplidos")
    requisitos_faltantes: List[RequisitosDiploma] = Field(default_factory=list, description="Requisitos pendientes")
    nota_promedio: Optional[float] = Field(None, description="Nota promedio en escala colombiana")
    horas_completadas: Optional[int] = Field(None, description="Horas académicas completadas")
    porcentaje_completado: Optional[float] = Field(None, description="Porcentaje de completitud del programa")
    mensaje: str = Field(..., description="Mensaje de estado")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")

class SolicitudDiploma(BaseModel):
    """Solicitud para generar un diploma colombiano"""
    email: EmailStr = Field(..., description="Email del estudiante")
    id_curso: str = Field(..., description="ID del curso para el diploma")
    tipo_diploma: str = Field("curso", description="Tipo de diploma a generar")
    forzar_generacion: bool = Field(False, description="Forzar generación aunque no se cumplan todos los requisitos")
    incluir_apostilla: bool = Field(False, description="Incluir proceso de apostilla")
    idioma: str = Field("es", description="Idioma del diploma (es, en)")
    formato_entrega: str = Field("digital", description="Formato de entrega (digital, fisico, ambos)")
    
    @validator('tipo_diploma')
    def validar_tipo_diploma_solicitud(cls, v):
        tipos_validos = ['curso', 'diplomado', 'certificacion', 'especializacion', 'tecnico', 'tecnologico']
        if v.lower() not in tipos_validos:
            raise ValueError(f'Tipo de diploma debe ser uno de: {tipos_validos}')
        return v.lower()
    
    @validator('idioma')
    def validar_idioma(cls, v):
        idiomas_validos = ['es', 'en']
        if v not in idiomas_validos:
            raise ValueError(f'Idioma debe ser uno de: {idiomas_validos}')
        return v

class ConfiguracionDiplomasColombia:
    """Configuración específica para diplomas en Colombia"""
    
    # Escalas de calificación
    ESCALA_NUMERICA_MIN: ClassVar[float] = 1.0
    ESCALA_NUMERICA_MAX: ClassVar[float] = 5.0
    NOTA_MINIMA_APROBACION: ClassVar[float] = 3.0
    
    # Tipos de diplomas válidos
    TIPOS_DIPLOMA: ClassVar[List[str]] = [
        'curso',
        'diplomado', 
        'certificacion',
        'especializacion',
        'tecnico',
        'tecnologico'
    ]
    
    # Niveles educativos
    NIVELES_EDUCATIVOS: ClassVar[List[str]] = [
        'Educación Continua',
        'Técnico Profesional',
        'Tecnológico',
        'Profesional',
        'Especialización',
        'Maestría',
        'Doctorado'
    ]
    
    # Modalidades
    MODALIDADES: ClassVar[List[str]] = [
        'Presencial',
        'Virtual',
        'Mixta',
        'A Distancia'
    ]
    
    # Mapeo de calificaciones
    CALIFICACIONES_CUALITATIVAS: ClassVar[Dict[tuple, str]] = {
        (4.6, 5.0): "Excelente",
        (4.0, 4.5): "Sobresaliente", 
        (3.5, 3.9): "Bueno",
        (3.0, 3.4): "Aceptable",
        (2.0, 2.9): "Insuficiente",
        (1.0, 1.9): "Deficiente"
    }
    
    @classmethod
    def obtener_calificacion_cualitativa(cls, nota: float) -> str:
        """Obtener calificación cualitativa basada en la nota numérica"""
        for (min_nota, max_nota), calificacion in cls.CALIFICACIONES_CUALITATIVAS.items():
            if min_nota <= nota <= max_nota:
                return calificacion
        return "No Aplica" 