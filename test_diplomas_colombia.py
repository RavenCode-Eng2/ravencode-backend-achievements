#!/usr/bin/env python3
"""
Script de pruebas para el Sistema de Diplomas Colombiano
RavenCode Achievements & Diplomas API v2.1.0

Este script demuestra todas las funcionalidades del sistema de diplomas
adaptado para Colombia con escala de notas 1.0-5.0.
"""

import requests
import json
from datetime import datetime

# URL base de la API
BASE_URL = "http://localhost:8003"

def imprimir_respuesta(titulo, response):
    """Función auxiliar para imprimir respuestas de la API de forma clara"""
    print(f"\n{'='*60}")
    print(f"{titulo}")
    print(f"{'='*60}")
    print(f"Código de Estado: {response.status_code}")
    try:
        response_json = response.json()
        print(f"Respuesta: {json.dumps(response_json, indent=2, default=str, ensure_ascii=False)}")
    except:
        print(f"Respuesta: {response.text}")

def test_configuracion_colombia():
    """Probar obtención de configuración del sistema colombiano"""
    response = requests.get(f"{BASE_URL}/diplomas/configuracion")
    imprimir_respuesta("🇨🇴 Configuración Sistema Diplomas Colombia", response)

def test_convertir_notas():
    """Probar conversión de porcentajes a notas colombianas"""
    porcentajes = [100, 95, 85, 75, 65, 55, 40]
    
    for porcentaje in porcentajes:
        response = requests.get(f"{BASE_URL}/diplomas/convertir-nota?porcentaje={porcentaje}")
        imprimir_respuesta(f"📊 Conversión {porcentaje}% a Nota Colombiana", response)

def test_crear_plantilla_diploma():
    """Crear una plantilla de diploma colombiano"""
    plantilla = {
        "tipo_diploma": "curso",
        "id_curso": "python_basico_colombia",
        "nombre_diploma": "Diplomado en Programación Python Básica",
        "titulo_diploma": "Certificado de Finalización Exitosa en Programación Python",
        "descripcion": "Programa de formación en programación Python adaptado al contexto colombiano",
        "institucion_emisora": "RavenCode Colombia",
        "requisitos": [
            {
                "nombre_logro": "fundamentos_python",
                "id_curso": "python_basico_colombia", 
                "nota_minima": 3.5,
                "es_obligatorio": True
            },
            {
                "nombre_logro": "proyecto_final",
                "id_curso": "python_basico_colombia",
                "nota_minima": 4.0,
                "es_obligatorio": True
            },
            {
                "nombre_logro": "evaluacion_integral",
                "id_curso": "python_basico_colombia",
                "nota_minima": 3.0,
                "es_obligatorio": True
            }
        ],
        "creditos_academicos": 3,
        "horas_academicas": 120,
        "modalidad": "Virtual",
        "nivel_educativo": "Educación Continua",
        "codigo_snies": None
    }
    
    response = requests.post(f"{BASE_URL}/diplomas/plantillas", json=plantilla)
    imprimir_respuesta("📜 Creación Plantilla Diploma Colombia", response)

def test_crear_logros_estudiante():
    """Crear logros para un estudiante de prueba"""
    email = "estudiante.colombia@example.com"
    
    logros = [
        {
            "achievement": {
                "achievement_name": "fundamentos_python",
                "course_id": "python_basico_colombia",
                "title": "Fundamentos de Python",
                "description": "Dominio de conceptos básicos de programación en Python",
                "metadata": {"xp": 100, "horas": 40, "categoria": "programacion"}
            },
            "score": 88.0,
            "total_points": 100.0
        },
        {
            "achievement": {
                "achievement_name": "proyecto_final",
                "course_id": "python_basico_colombia",
                "title": "Proyecto Final",
                "description": "Desarrollo exitoso del proyecto final del curso",
                "metadata": {"xp": 150, "horas": 50, "categoria": "proyecto"}
            },
            "score": 92.0,
            "total_points": 100.0
        },
        {
            "achievement": {
                "achievement_name": "evaluacion_integral",
                "course_id": "python_basico_colombia",
                "title": "Evaluación Integral",
                "description": "Evaluación comprehensiva de conocimientos",
                "metadata": {"xp": 80, "horas": 30, "categoria": "evaluacion"}
            },
            "score": 78.0,
            "total_points": 100.0
        }
    ]
    
    for i, logro_data in enumerate(logros):
        logro_data["email"] = email
        response = requests.post(f"{BASE_URL}/achievements/update", json=logro_data)
        imprimir_respuesta(f"🎯 Crear Logro {i+1} para Estudiante Colombia", response)

def test_verificar_elegibilidad():
    """Verificar elegibilidad de estudiante para diploma"""
    email = "estudiante.colombia@example.com"
    response = requests.get(
        f"{BASE_URL}/diplomas/verificar-elegibilidad/{email}",
        params={"id_curso": "python_basico_colombia", "tipo_diploma": "curso"}
    )
    imprimir_respuesta("✅ Verificación Elegibilidad Diploma", response)

def test_generar_diploma():
    """Generar diploma colombiano"""
    solicitud = {
        "email": "estudiante.colombia@example.com",
        "id_curso": "python_basico_colombia",
        "tipo_diploma": "curso",
        "forzar_generacion": False,
        "incluir_apostilla": False,
        "idioma": "es",
        "formato_entrega": "digital"
    }
    
    response = requests.post(f"{BASE_URL}/diplomas/generar", json=solicitud)
    imprimir_respuesta("🎓 Generación Diploma Colombia", response)

def test_obtener_diplomas_estudiante():
    """Obtener diplomas de un estudiante"""
    email = "estudiante.colombia@example.com"
    response = requests.get(f"{BASE_URL}/diplomas/estudiante/{email}")
    imprimir_respuesta("📋 Diplomas del Estudiante", response)

def test_verificar_diploma():
    """Verificar diploma por código (primero necesitamos obtener un código)"""
    # Primero obtenemos los diplomas del estudiante para obtener un código
    email = "estudiante.colombia@example.com"
    response = requests.get(f"{BASE_URL}/diplomas/estudiante/{email}")
    
    if response.status_code == 200:
        data = response.json()
        diplomas = data.get("data", {}).get("diplomas", [])
        
        if diplomas:
            codigo_verificacion = diplomas[0].get("codigo_verificacion")
            if codigo_verificacion:
                verify_response = requests.get(f"{BASE_URL}/diplomas/verificar/{codigo_verificacion}")
                imprimir_respuesta("🔍 Verificación Autenticidad Diploma", verify_response)
            else:
                print("❌ No se encontró código de verificación")
        else:
            print("❌ No se encontraron diplomas para verificar")
    else:
        print("❌ Error obteniendo diplomas del estudiante")

def test_estadisticas_diplomas():
    """Obtener estadísticas del sistema de diplomas"""
    response = requests.get(f"{BASE_URL}/diplomas/estadisticas")
    imprimir_respuesta("📊 Estadísticas Sistema Diplomas", response)

def test_estudiante_sin_requisitos():
    """Probar con estudiante que no cumple requisitos"""
    email = "estudiante.incompleto@example.com"
    
    # Crear solo un logro parcial
    logro_parcial = {
        "email": email,
        "achievement": {
            "achievement_name": "fundamentos_python",
            "course_id": "python_basico_colombia",
            "title": "Fundamentos de Python",
            "description": "Intento de fundamentos",
            "metadata": {"xp": 50, "horas": 20}
        },
        "score": 65.0,  # Nota insuficiente (2.6 en escala colombiana)
        "total_points": 100.0
    }
    
    response = requests.post(f"{BASE_URL}/achievements/update", json=logro_parcial)
    imprimir_respuesta("📝 Crear Logro Insuficiente", response)
    
    # Verificar elegibilidad (debe fallar)
    response = requests.get(
        f"{BASE_URL}/diplomas/verificar-elegibilidad/{email}",
        params={"id_curso": "python_basico_colombia", "tipo_diploma": "curso"}
    )
    imprimir_respuesta("❌ Verificación Elegibilidad (Insuficiente)", response)

def test_endpoints_principales():
    """Probar endpoints principales de la API"""
    response = requests.get(f"{BASE_URL}/")
    imprimir_respuesta("🏠 Endpoint Principal", response)
    
    response = requests.get(f"{BASE_URL}/health")
    imprimir_respuesta("❤️ Health Check", response)

def ejecutar_todas_las_pruebas():
    """Ejecutar todas las pruebas del sistema de diplomas"""
    print("🚀 Iniciando Pruebas del Sistema de Diplomas Colombia")
    print(f"🌐 Probando API en: {BASE_URL}")
    print("🇨🇴 Sistema adaptado para Colombia con escala de notas 1.0-5.0")
    
    pruebas = [
        test_endpoints_principales,
        test_configuracion_colombia,
        test_convertir_notas,
        test_crear_plantilla_diploma,
        test_crear_logros_estudiante,
        test_verificar_elegibilidad,
        test_generar_diploma,
        test_obtener_diplomas_estudiante,
        test_verificar_diploma,
        test_estadisticas_diplomas,
        test_estudiante_sin_requisitos
    ]
    
    for prueba in pruebas:
        try:
            prueba()
        except requests.exceptions.ConnectionError:
            print(f"\n❌ No se pudo conectar a la API en {BASE_URL}")
            print("Asegúrate de que el servidor esté ejecutándose con: python startup.py")
            break
        except Exception as e:
            print(f"\n❌ Error en {prueba.__name__}: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 Pruebas completadas!")
    print("📚 Documentación disponible en: http://localhost:8003/docs")
    print("🇨🇴 Sistema de Diplomas Colombia listo para producción")
    print(f"{'='*60}")

if __name__ == "__main__":
    ejecutar_todas_las_pruebas() 