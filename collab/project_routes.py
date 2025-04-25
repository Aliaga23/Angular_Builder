from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Project
from pydantic import BaseModel
from typing import Optional
from uuid import UUID, uuid4

router = APIRouter(prefix="/api/projects", tags=["projects"])

# Modelo de entrada para crear/actualizar
class ProjectSchema(BaseModel):
    name: str
    owner_id: UUID
    data: dict

@router.post("/")
def create_project(payload: ProjectSchema, db: Session = Depends(get_db)):
    new_project = Project(
        id=uuid4(),  # Se genera aquí automáticamente
        name=payload.name,
        owner_id=payload.owner_id,
        data=payload.data
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {
        "message": "Proyecto creado",
        "project_id": str(new_project.id)
    }

@router.put("/{project_id}")
def update_project(project_id: UUID, payload: ProjectSchema, db: Session = Depends(get_db)):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    project.name = payload.name
    project.owner_id = payload.owner_id
    project.data = payload.data
    db.commit()
    return {"message": "Proyecto actualizado"}

@router.get("/{project_id}")
def get_project(project_id: UUID, db: Session = Depends(get_db)):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {
        "id": str(project.id),
        "name": project.name,
        "owner_id": str(project.owner_id),
        "data": project.data,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }

@router.delete("/{project_id}")
def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    db.delete(project)
    db.commit()
    return {"message": "Proyecto eliminado"}


@router.get("/user/{user_id}")
def get_projects_by_user(user_id: UUID, db: Session = Depends(get_db)):
    projects = db.query(Project).filter_by(owner_id=user_id).all()
    if not projects:
        return {"message": "No se encontraron proyectos para este usuario", "projects": []}

    return {
        "projects": [
            {
                "id": str(p.id),
                "name": p.name,
                "owner_id": str(p.owner_id),
                "data": p.data,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
            }
            for p in projects
        ]
    }
