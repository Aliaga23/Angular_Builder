from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from generator.models import AngularAppSchema
from generator.angular_project_builder import generar_proyecto_angular
from collab.router import router as collab_router

from db.models import Base  # <-- IMPORT DB
from db.database import engine  # <-- IMPORT ENGINE
from auth.routes import router as auth_router


app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generar-angular/")
def generar_app(data: AngularAppSchema):
    try:
        zip_path = generar_proyecto_angular(data)
        return FileResponse(path=zip_path, filename="angular-ui-app.zip", media_type="application/zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el proyecto: {str(e)}")

# Rutas de colaboración en tiempo real
app.include_router(collab_router)
app.include_router(auth_router)

