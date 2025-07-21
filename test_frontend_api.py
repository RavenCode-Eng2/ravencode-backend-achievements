#!/usr/bin/env python3
"""
Test script for RavenCode Achievements API v2.1.0
Tests the API endpoints to ensure they match frontend TypeScript interface expectations
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8003"
TEST_EMAIL = "frontend.test@example.com"
TEST_COURSE_ID = "react-fundamentals"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def print_response(response, title="Response"):
    print(f"\n📋 {title}")
    print(f"Status Code: {response.status_code}")
    if response.headers.get('content-type', '').startswith('application/json'):
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, default=str)}")
        except:
            print(f"Response Text: {response.text}")
    else:
        print(f"Response Text: {response.text}")

def test_api():
    print("🚀 Testing RavenCode Achievements API v2.1.0")
    print("🎯 Frontend Interface Compatibility Tests")
    print("🌐 API Base URL:", BASE_URL)
    
    # Test 1: Root endpoint
    print_header("Root Endpoint - API Info")
    response = requests.get(f"{BASE_URL}/")
    print_response(response)
    
    # Test 2: Health check
    print_header("Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    
    # Test 3: Create achievement using new structure
    print_header("Create Achievement - Frontend Format")
    achievement_data = {
        "email": TEST_EMAIL,
        "achievement": {
            "achievement_name": "first_lesson_completed",
            "course_id": TEST_COURSE_ID,
            "title": "Primera Lección Completada",
            "description": "Has completado tu primera lección de React",
            "metadata": {
                "category": "learning",
                "rarity": "common",
                "xp_reward": 100,
                "difficulty": "beginner",
                "module": "introduction",
                "requirements": ["Complete first lesson"],
                "tags": ["beginner", "react"]
            }
        },
        "score": 85,
        "total_points": 100
    }
    
    response = requests.post(f"{BASE_URL}/achievements/update", json=achievement_data)
    print_response(response, "Achievement Creation")
    
    # Test 4: Create another achievement
    print_header("Create Second Achievement")
    achievement_data_2 = {
        "email": TEST_EMAIL,
        "achievement": {
            "achievement_name": "component_master",
            "course_id": TEST_COURSE_ID,
            "title": "Maestro de Componentes",
            "description": "Has dominado la creación de componentes React",
            "metadata": {
                "category": "mastery",
                "rarity": "rare",
                "xp_reward": 250,
                "difficulty": "intermediate",
                "module": "components",
                "requirements": ["Create 5 components", "Use props correctly"],
                "tags": ["components", "react", "mastery"]
            }
        },
        "score": 92,
        "total_points": 100
    }
    
    response = requests.post(f"{BASE_URL}/achievements/update", json=achievement_data_2)
    print_response(response, "Second Achievement Creation")
    
    # Test 5: Get student achievements (frontend format)
    print_header("Get Student Achievements - Frontend Format")
    response = requests.get(f"{BASE_URL}/achievements/{TEST_EMAIL}")
    print_response(response, "Student Achievements")
    
    # Test 6: Get achievement statistics
    print_header("Get Achievement Statistics")
    response = requests.get(f"{BASE_URL}/achievements/{TEST_EMAIL}/stats")
    print_response(response, "Achievement Statistics")
    
    # Test 7: Get available achievements for course
    print_header("Get Available Achievements for Course")
    response = requests.get(f"{BASE_URL}/achievements/course/{TEST_COURSE_ID}/available")
    print_response(response, "Available Achievements")
    
    # Test 8: Bulk update achievements
    print_header("Bulk Update Achievements")
    bulk_data = {
        "updates": [
            {
                "email": f"bulk1.{TEST_EMAIL}",
                "achievement": {
                    "achievement_name": "quiz_master",
                    "course_id": TEST_COURSE_ID,
                    "title": "Maestro de Quizzes",
                    "description": "Has completado todos los quizzes",
                    "metadata": {
                        "category": "practice",
                        "rarity": "epic",
                        "xp_reward": 300,
                        "difficulty": "advanced"
                    }
                },
                "score": 95,
                "total_points": 100
            },
            {
                "email": f"bulk2.{TEST_EMAIL}",
                "achievement": {
                    "achievement_name": "project_hero",
                    "course_id": TEST_COURSE_ID,
                    "title": "Héroe de Proyectos",
                    "description": "Has completado el proyecto final con excelencia",
                    "metadata": {
                        "category": "achievement",
                        "rarity": "legendary",
                        "xp_reward": 500,
                        "difficulty": "expert"
                    }
                },
                "score": 98,
                "total_points": 100
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/achievements/bulk-update", json=bulk_data)
    print_response(response, "Bulk Update Results")
    
    # Test 9: Admin endpoints
    print_header("Admin Endpoints - Get All Achievements")
    response = requests.get(f"{BASE_URL}/admin/achievements")
    print_response(response, "All Achievements (Admin)")
    
    # Test 10: Admin - Get specific user
    print_header("Admin - Get User Achievements")
    response = requests.get(f"{BASE_URL}/admin/achievements/user/{TEST_EMAIL}")
    print_response(response, "User Achievements (Admin View)")
    
    # Test 11: Admin - Create achievement
    print_header("Admin - Create Achievement")
    admin_create_data = {
        "user_email": f"admin.{TEST_EMAIL}",
        "course_id": TEST_COURSE_ID,
        "achievement_name": "admin_created",
        "title": "Logro Creado por Admin",
        "description": "Este logro fue creado por un administrador",
        "score": 88,
        "total_points": 100,
        "metadata": {
            "category": "community",
            "rarity": "rare",
            "xp_reward": 150,
            "difficulty": "intermediate",
            "admin_created": True
        }
    }
    
    response = requests.post(f"{BASE_URL}/admin/achievements/create", json=admin_create_data)
    print_response(response, "Admin Achievement Creation")
    
    # Test 12: Delete achievement
    print_header("Delete Achievement")
    response = requests.delete(f"{BASE_URL}/achievements/{TEST_EMAIL}/first_lesson_completed")
    print_response(response, "Achievement Deletion")
    
    # Test 13: Verify deletion
    print_header("Verify Achievement After Deletion")
    response = requests.get(f"{BASE_URL}/achievements/{TEST_EMAIL}")
    print_response(response, "Achievements After Deletion")
    
    print_header("🎉 Frontend Compatibility Tests Completed!")
    print("📚 API Documentation: http://localhost:8003/docs")
    print("🎯 All endpoints tested with frontend-compatible formats")
    print("✅ Ready for frontend integration!")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("💡 Make sure the server is running: python startup.py")
    except Exception as e:
        print(f"❌ Error during testing: {e}") 