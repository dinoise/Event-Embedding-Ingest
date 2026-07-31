# main.py (corregido)
import functions_framework
from base64 import b64decode
from dotenv import load_dotenv
from os import getenv
from typing import List
from uuid import uuid4
from datetime import datetime

from langchain_google_vertexai import VertexAIEmbeddings

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
        event_message = data.decode("utf-8")
        print("Mensaje recibido:", event_message)

        # Generar embedding real a partir del mensaje
        embedding_service = VertexAIEmbeddings(
            model_name=current_config.EMBEDDING_MODEL_NAME
        )
        embedded_message: List[float] = embedding_service.embed_query(event_message)

        # Ejecutar lógica
        success, message = EventController.create_event(
            event_uuid=uuid4(),  # Genera un nuevo UUID
            event_message=event_message,
            embedded_message=embedded_message,
            timestamp=datetime.utcnow()
        )

        if success:
            print("OK", message)
        else:
            print("ERROR", message)
    except Exception as e:
        print(f"Error crítico: {str(e)}")
        return f"Error: {str(e)}", 500
