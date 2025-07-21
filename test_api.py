#!/usr/bin/env python3
"""
Test script for RavenCode Achievements API v2.0.0

This script demonstrates all the new endpoints and features implemented.
Run this after starting the API server to test functionality.
"""

import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8003"

def print_response(title, response):
    """Helper function to print API responses nicely"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    try:
        response_json = response.json()
        print(f"Response: {json.dumps(response_json, indent=2, default=str)}")
    except:
        print(f"Response: {response.text}")

def test_root_endpoint():
    """Test the root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print_response("Testing Root Endpoint", response)

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("Testing Health Check", response)

def test_update_achievement():
    """Test updating/creating an achievement"""
    achievement_data = {
        "email": "student@example.com",
        "achievement": {
            "achievement_name": "first_lesson_completed",
            "course_id": "python_basics",
            "title": "First Lesson Completed",
            "description": "Completed the first lesson in Python Basics",
            "metadata": {
                "xp": 50,
                "category": "beginner",
                "difficulty": "easy"
            }
        },
        "score": 85.0,
        "total_points": 100.0
    }
    
    response = requests.post(f"{BASE_URL}/achievements/update", json=achievement_data)
    print_response("Testing Achievement Update", response)

def test_get_achievements():
    """Test getting student achievements"""
    response = requests.get(f"{BASE_URL}/achievements/student@example.com")
    print_response("Testing Get Student Achievements", response)

def test_get_achievement_stats():
    """Test getting achievement statistics"""
    response = requests.get(f"{BASE_URL}/achievements/student@example.com/stats")
    print_response("Testing Achievement Statistics", response)

def test_get_course_achievements():
    """Test getting available achievements for a course"""
    response = requests.get(f"{BASE_URL}/achievements/course/python_basics/available")
    print_response("Testing Course Available Achievements", response)

def test_bulk_update():
    """Test bulk achievement updates"""
    bulk_data = {
        "updates": [
            {
                "email": "student@example.com",
                "achievement": {
                    "achievement_name": "module_completed",
                    "course_id": "python_basics",
                    "title": "Module Completed",
                    "description": "Completed a full module",
                    "metadata": {"xp": 100, "category": "intermediate"}
                },
                "score": 90.0,
                "total_points": 100.0
            },
            {
                "email": "student2@example.com",
                "achievement": {
                    "achievement_name": "first_lesson_completed",
                    "course_id": "python_basics",
                    "title": "First Lesson Completed",
                    "description": "Completed the first lesson",
                    "metadata": {"xp": 50, "category": "beginner"}
                },
                "score": 95.0,
                "total_points": 100.0
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/achievements/bulk-update", json=bulk_data)
    print_response("Testing Bulk Achievement Update", response)

def test_invalid_data():
    """Test validation with invalid data"""
    invalid_data = {
        "email": "invalid-email",  # Invalid email format
        "achievement": {
            "achievement_name": "",  # Empty achievement name
            "course_id": "python_basics",
            "title": "Test"
        },
        "score": 150.0,  # Score greater than total_points
        "total_points": 100.0
    }
    
    response = requests.post(f"{BASE_URL}/achievements/update", json=invalid_data)
    print_response("Testing Invalid Data Validation", response)

def test_delete_achievement():
    """Test deleting an achievement"""
    response = requests.delete(f"{BASE_URL}/achievements/student@example.com/module_completed")
    print_response("Testing Achievement Deletion", response)

def test_nonexistent_student():
    """Test getting achievements for non-existent student"""
    response = requests.get(f"{BASE_URL}/achievements/nonexistent@example.com")
    print_response("Testing Non-existent Student", response)

def run_all_tests():
    """Run all test functions"""
    print("🚀 Starting RavenCode Achievements API v2.0.0 Tests")
    print(f"Testing API at: {BASE_URL}")
    
    tests = [
        test_root_endpoint,
        test_health_check,
        test_update_achievement,
        test_get_achievements,
        test_get_achievement_stats,
        test_get_course_achievements,
        test_bulk_update,
        test_invalid_data,
        test_delete_achievement,
        test_nonexistent_student
    ]
    
    for test_func in tests:
        try:
            test_func()
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Could not connect to API at {BASE_URL}")
            print("Make sure the API server is running with: python -m app.main")
            break
        except Exception as e:
            print(f"\n❌ Error in {test_func.__name__}: {e}")
    
    print(f"\n{'='*50}")
    print("🎉 Test run completed!")
    print("Check the responses above to verify functionality.")
    print(f"{'='*50}")

if __name__ == "__main__":
    run_all_tests() 