#!/usr/bin/env python3
"""
Startup script for RavenCode Achievements API

This script:
1. Tests database connection
2. Creates necessary indexes
3. Starts the API server

Usage: python startup.py
"""

import sys
import time
from app.DB.database import test_connection
from app.DB.initialize import optimize_database
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main startup function"""
    logger.info("🚀 Starting RavenCode Achievements API v2.0.0")
    
    # Test database connection
    logger.info("📡 Testing database connection...")
    if not test_connection():
        logger.error("❌ Database connection failed. Please check your MongoDB configuration.")
        logger.error("Make sure MongoDB is running and MONGODB_URL is correct in your .env file")
        sys.exit(1)
    
    # Initialize database
    logger.info("🗄️  Initializing database indexes...")
    if not optimize_database():
        logger.warning("⚠️  Database optimization failed, but continuing...")
    else:
        logger.info("✅ Database optimization completed")
    
    # Start the API server
    logger.info("🌟 Starting API server on http://localhost:8003")
    logger.info("📚 API Documentation available at: http://localhost:8003/docs")
    logger.info("🔧 Alternative docs at: http://localhost:8003/redoc")
    logger.info("❤️  Health check at: http://localhost:8003/health")
    logger.info("🧪 Run tests with: python test_api.py")
    
    try:
        # Start uvicorn server
        from app.main import app
        import uvicorn
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8003,
            log_level="info",
            reload=False  # Set to True for development
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 