from datetime import datetime
from uuid import UUID
from __init__ import get_db_session
from models import EventEmbedding
from sqlalchemy.exc import SQLAlchemyError

class EventController:
    
    @staticmethod
    def create_event(
        event_uuid: UUID,
        event_message: str,
        embedded_message: list[float],
        timestamp: datetime = None
    ) -> tuple[bool, str]:
        """
        Crea un nuevo evento en la base de datos
        
        Args:
            event_uuid: UUID único para el evento
            event_message: Mensaje original del evento
            embedded_message: Vector de embeddings (debe ser lista de 768 floats)
            timestamp: Opcional. Si no se provee, usa la hora actual
            
        Returns:
            tuple: (success: bool, message: str)
        """
        session = get_db_session()
        
        try:
            # Validaciones
            if len(embedded_message) != 768:
                return False, f"El vector de embeddings debe tener exactamente 768 dimensiones. El vector de entrada tiene tamaño {len(embedded_message)}"
            
            if not timestamp:
                timestamp = datetime.utcnow()
            
            # Crear objeto
            new_event = EventEmbedding(
                event_uuid=event_uuid,
                embedding_event_message=event_message,
                embedding_embedded_message=embedded_message,
                embedding_timestamp=timestamp
            )
            
            # Guardar en DB
            session.add(new_event)
            session.commit()
            
            return True, "Evento creado exitosamente"
            
        except ValueError as e:
            session.rollback()
            return False, f"Error de validación: {str(e)}"
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            session.rollback()
            return False, f"Error inesperado: {str(e)}"
        finally:
            session.remove()