from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Project
from pydantic import BaseModel
from typing import Optional
from uuid import UUID, uuid4
from db.models import UserProjectAccess,  User
from db.database import get_db
from auth.dependencies import get_current_user  # asegúrate de que este archivo exista
from typing import List

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

@router.post("/accept-invite/{project_id}")
def accept_invite(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar que el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # Verificar si el usuario ya tiene acceso
    existing = db.query(UserProjectAccess).filter_by(
        user_id=current_user.id,
        project_id=project_id
    ).first()

    if existing:
        return {"message": "Ya tienes acceso a este proyecto"}

    # Conceder acceso
    new_access = UserProjectAccess(user_id=current_user.id, project_id=project_id)
    db.add(new_access)
    db.commit()

    return {"message": "Acceso concedido correctamente"}


@router.get("/shared", response_model=List[dict])
def get_shared_projects(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Obtener proyectos a los que el usuario tiene acceso
    shared_projects = (
        db.query(Project)
        .join(UserProjectAccess, Project.id == UserProjectAccess.project_id)
        .filter(UserProjectAccess.user_id == current_user.id)
        .all()
    )

    return [
        {
            "id": str(p.id),
            "name": p.name,
            "owner_id": str(p.owner_id),
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        for p in shared_projects
    ]