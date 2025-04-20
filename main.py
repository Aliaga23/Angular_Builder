from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from generator.models import AngularAppSchema
from generator.angular_project_builder import generar_proyecto_angular

app = FastAPI()

@app.post("/generar-angular/")
def generar_app(data: AngularAppSchema):
    try:
        zip_path = generar_proyecto_angular(data)
        return FileResponse(path=zip_path, filename="angular-ui-app.zip", media_type="application/zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el proyecto: {str(e)}")
