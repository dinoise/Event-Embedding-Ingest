from __init__ import Base

from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, String

class EventEmbedding(Base):
    __tablename__ = 'tb_lvp_event_embeddings'

    event_uuid = Column(UUID(as_uuid=True), primary_key=True)
    embedding_event_message = Column(String)
    embedding_embedded_message = Column(Vector(768), nullable=False)
    embedding_timestamp = Column(DateTime(timezone=True))