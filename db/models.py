from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
import uuid
import datetime
from sqlalchemy import PrimaryKeyConstraint
Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    email = Column(String, unique=True)
    password = Column(String, nullable=False)  # 🔸 Campo nuevo requerido
    color = Column(String, default="#3b82f6")
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

class Project(Base):
    __tablename__ = "project"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Nuevo campo para guardar todo el estado del proyecto como JSON
    data = Column(JSONB, nullable=False)

class UserProjectAccess(Base):
    __tablename__ = "user_project_access"
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    granted_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'project_id'),
    )
