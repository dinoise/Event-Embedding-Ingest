# config.py
from os import getenv

class Config:
    """Configuraciones comunes"""
    FLASK_ENV = getenv("FLASK_ENV", "dev")
    PROJECT_ID = getenv("GOOGLE_CLOUD_PROJECT")
    EMBEDDING_MODEL_NAME = getenv("EMBEDDING_MODEL_NAME")
    
class DevelopmentConfig(Config):
    """Configuraciones para desarrollo"""
    DATASET_DELIVERNOW = "BQ_DS_RAW_DELIVERNOW_DEV"

    # Dectect if we are in local (CLOUD_VAR is a variable defined in Cloud Run)
    IS_NOT_LOCAL = getenv("CLOUD_VAR") is not None
    
    # Configuration for POSTGRE
    DB_HOST = "POSTGRE_IP_PRIVATE" if IS_NOT_LOCAL else "POSTGRE_IP_PUBLIC"
    DB_PORT = "POSTGRE_PORT"
    DB_USER = "POSTGRE_USR_RAG_REPO_DEV"
    DB_PASSWORD = "POSTGRE_PASS_RAG_REPO_DEV"
    DB_NAME = "POSTGRE_DB_RAG_REPO"

class ProductionConfig(Config):
    """Configuraciones para producción"""
    DATASET_DELIVERNOW = "BQ_DS_RAW_DELIVERNOW_DEV"

    # Configuration for POSTGRE
    DB_HOST = "POSTGRE_IP_PRIVATE"
    DB_PASSWORD = "POSTGRE_PASS_RAG_REPO_DEV"
    DB_NAME = "POSTGRE_DB_RAG_REPO"

# Dictionary to select the environment
config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig
}