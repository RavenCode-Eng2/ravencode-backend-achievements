from app.DB.database import get_database
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_indexes():
    """Create database indexes for better performance"""
    try:
        db = get_database()
        if db is None:
            logger.error("Could not connect to database")
            return False
        
        students_collection = db["students"]
        diplomas_collection = db["diplomas"]
        plantillas_diplomas_collection = db["plantillas_diplomas"]
        
        # Create indexes for students collection
        indexes_to_create = [
            # Unique index on email
            {"keys": [("email", 1)], "unique": True, "name": "email_unique"},
            
            # Compound index for email and achievement_name
            {"keys": [("email", 1), ("achievements.achievement_name", 1)], "name": "email_achievement_name"},
            
            # Index on course_id for achievements
            {"keys": [("achievements.course_id", 1)], "name": "achievements_course_id"},
            
            # Index on achievement status
            {"keys": [("achievements.status", 1)], "name": "achievements_status"},
            
            # Index on date_earned for recent achievements
            {"keys": [("achievements.date_earned", -1)], "name": "achievements_date_earned_desc"},
            
            # Index on achieved status
            {"keys": [("achievements.achieved", 1)], "name": "achievements_achieved"},
            
            # Index on updated_at for tracking
            {"keys": [("updated_at", -1)], "name": "updated_at_desc"},
        ]
        
        created_count = 0
        for index_spec in indexes_to_create:
            try:
                students_collection.create_index(
                    index_spec["keys"],
                    unique=index_spec.get("unique", False),
                    name=index_spec["name"],
                    background=True  # Create index in background
                )
                logger.info(f"Created index: {index_spec['name']}")
                created_count += 1
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"Index {index_spec['name']} already exists")
                else:
                    logger.error(f"Error creating index {index_spec['name']}: {e}")
        
        # Create indexes for diplomas collection
        diploma_indexes = [
            # Unique index on email + course_id + tipo_diploma
            {"keys": [("email", 1), ("id_curso", 1), ("tipo_diploma", 1)], "unique": True, "name": "diploma_unique"},
            
            # Index on verification code
            {"keys": [("codigo_verificacion", 1)], "unique": True, "name": "codigo_verificacion_unique"},
            
            # Index on student email
            {"keys": [("email", 1)], "name": "diploma_email"},
            
            # Index on course_id
            {"keys": [("id_curso", 1)], "name": "diploma_course_id"},
            
            # Index on diploma type
            {"keys": [("tipo_diploma", 1)], "name": "diploma_type"},
            
            # Index on fecha_obtencion (descending for recent diplomas)
            {"keys": [("fecha_obtencion", -1)], "name": "diploma_fecha_obtencion_desc"},
            
            # Index on fecha_vencimiento for expired diplomas
            {"keys": [("fecha_vencimiento", 1)], "name": "diploma_fecha_vencimiento"},
            
            # Index on nota_final for statistics
            {"keys": [("nota_final", 1)], "name": "diploma_nota_final"},
        ]
        
        for index_spec in diploma_indexes:
            try:
                diplomas_collection.create_index(
                    index_spec["keys"],
                    unique=index_spec.get("unique", False),
                    name=index_spec["name"],
                    background=True
                )
                logger.info(f"Created diploma index: {index_spec['name']}")
                created_count += 1
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"Diploma index {index_spec['name']} already exists")
                else:
                    logger.error(f"Error creating diploma index {index_spec['name']}: {e}")
        
        # Create indexes for diploma templates collection
        template_indexes = [
            # Unique index on course_id + tipo_diploma
            {"keys": [("id_curso", 1), ("tipo_diploma", 1)], "unique": True, "name": "plantilla_unique"},
            
            # Index on course_id
            {"keys": [("id_curso", 1)], "name": "plantilla_course_id"},
            
            # Index on tipo_diploma
            {"keys": [("tipo_diploma", 1)], "name": "plantilla_tipo_diploma"},
        ]
        
        for index_spec in template_indexes:
            try:
                plantillas_diplomas_collection.create_index(
                    index_spec["keys"],
                    unique=index_spec.get("unique", False),
                    name=index_spec["name"],
                    background=True
                )
                logger.info(f"Created template index: {index_spec['name']}")
                created_count += 1
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"Template index {index_spec['name']} already exists")
                else:
                    logger.error(f"Error creating template index {index_spec['name']}: {e}")
        
        logger.info(f"Database indexes initialization completed. Created {created_count} new indexes.")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database indexes: {e}")
        return False

def optimize_database():
    """Run database optimization commands"""
    try:
        db = get_database()
        if db is None:
            logger.error("Could not connect to database")
            return False
        
        students_collection = db["students"]
        diplomas_collection = db["diplomas"]
        plantillas_diplomas_collection = db["plantillas_diplomas"]
        
        # Get collection stats
        students_stats = db.command("collStats", "students")
        logger.info(f"Students collection stats: {students_stats.get('count', 0)} documents, {students_stats.get('size', 0)} bytes")
        
        try:
            diplomas_stats = db.command("collStats", "diplomas")
            logger.info(f"Diplomas collection stats: {diplomas_stats.get('count', 0)} documents, {diplomas_stats.get('size', 0)} bytes")
        except:
            logger.info("Diplomas collection doesn't exist yet - will be created when first diploma is generated")
        
        try:
            templates_stats = db.command("collStats", "plantillas_diplomas")
            logger.info(f"Diploma templates collection stats: {templates_stats.get('count', 0)} documents, {templates_stats.get('size', 0)} bytes")
        except:
            logger.info("Diploma templates collection doesn't exist yet - will be created when first template is created")
        
        # Create any missing indexes
        create_indexes()
        
        logger.info("Database optimization completed")
        return True
        
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting database initialization...")
    success = optimize_database()
    if success:
        logger.info("Database initialization completed successfully")
    else:
        logger.error("Database initialization failed") 