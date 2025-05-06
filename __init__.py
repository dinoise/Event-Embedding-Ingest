# __init__.py
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from urllib.parse import quote_plus
from utils.utils import get_secret

# Inicializa primero la Base
Base = declarative_base()

# Variables globales (serán configuradas en init_db)
engine = None
db_session = None  # Cambiamos el nombre para evitar confusión

def init_db(config):
    global engine, db_session

    DB_HOST = get_secret(config.DB_HOST)
    DB_PORT = get_secret(config.DB_PORT)
    DB_USER = get_secret(config.DB_USER)
    DB_PASSWORD = get_secret(config.DB_PASSWORD)
    DB_NAME = get_secret(config.DB_NAME)

    if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME]):
        raise ValueError("Faltan valores de configuración de la base de datos")

    encoded_password = quote_plus(DB_PASSWORD)
    uri = f'postgresql+psycopg2://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    try:
        engine = create_engine(uri)
        # Configura la sesión
        db_session = scoped_session(sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        ))
        
        # Conecta la Base con el engine
        Base.metadata.bind = engine
        
        # Prueba la conexión
        with engine.connect() as conn:
            print("✅ Conexión a la base de datos establecida correctamente")
            
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        raise

# Exporta la sesión para usar en otros módulos
def get_db_session():
    if db_session is None:
        raise RuntimeError("La base de datos no ha sido inicializada. Llama a init_db() primero.")
    return db_session