from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env si existe
load_dotenv()

# Configuración de la conexión a MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ravencode_achievements_db")

def get_database():
    """
    Crea y retorna una conexión a la base de datos MongoDB.
    Conecta a la base de datos especificada por DATABASE_NAME usando MONGODB_URL.
    Devuelve:
        db (Database): El objeto de base de datos de MongoDB si la conexión es exitosa, None en caso contrario.
    También imprime un mensaje indicando el estado de la conexión.
    """
    try:
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        # Probar la conexión
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def test_connection():
    """
    Prueba la conexión a MongoDB y retorna True si es exitosa, False en caso contrario.
    Imprime un mensaje indicando el resultado del intento de conexión.
    Devuelve:
        bool: True si la conexión es exitosa, False en caso contrario.
    """
    try:
        client = MongoClient(MONGODB_URL)
        # Probar la conexión
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def close_database(client: MongoClient):
    """
    Cierra la conexión a la base de datos MongoDB.
    Args:
        client (MongoClient): La instancia de MongoClient a cerrar.
    Imprime un mensaje cuando la conexión se cierra.
    """
    if client:
        client.close()
        print("MongoDB connection closed.") 