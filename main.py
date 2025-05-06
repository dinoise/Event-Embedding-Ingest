# main.py (corregido)
import functions_framework
from base64 import b64decode
from dotenv import load_dotenv
from os import getenv

from __init__ import init_db
from config import config_by_name
from controller import EventController

@functions_framework.cloud_event
def main(cloud_event):
    try:
        print("Iniciando función...")
        load_dotenv()
        
        env = getenv("ENV", "dev")
        current_config = config_by_name[env]
        
        # Inicializar DB
        init_db(current_config)
        
        # Procesar mensaje
        data = b64decode(cloud_event.data["message"]["data"])
        print("Mensaje recibido:", data)
        
        # Ejecutar lógica
        from uuid import uuid4
        from datetime import datetime
        success, message = EventController.create_event(
            event_uuid=uuid4(),  # Genera un nuevo UUID
            event_message="Mensaje de prueba",
            embedded_message=[0.5] * 768,  # Vector de ejemplo con 768 dimensiones
            timestamp=datetime.utcnow()
        )

        if success:
            print("OK", message)
        else:
            print("ERROR", message)
    except Exception as e:
        print(f"Error crítico: {str(e)}")
        return f"Error: {str(e)}", 500