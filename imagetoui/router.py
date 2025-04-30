from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil
from imagetoui.utils.gemini import analizar_mockup
from imagetoui.utils.angular_gen import generar_angular, comprimir_proyecto

router = APIRouter(prefix="/generar-ui", tags=["Generador Angular"])

@router.post("/")
async def generar_angular_desde_mockup(
    imagen: UploadFile = File(...), 
    background_tasks: BackgroundTasks = None
):
    ruta_temp = "mockup.png"
    output_dir = "output"
    proyecto_path = os.path.join(output_dir, "angular_proyecto")
    zip_path = os.path.join(output_dir, "angular_proyecto.zip")

    # Guardar imagen temporal
    with open(ruta_temp, "wb") as f:
        f.write(await imagen.read())

    descripcion_ui = analizar_mockup(ruta_temp)
    generar_angular(descripcion_ui, proyecto_path)
    comprimir_proyecto(proyecto_path, zip_path)

    # Agregar tareas de limpieza en segundo plano
    background_tasks.add_task(os.remove, ruta_temp)
    background_tasks.add_task(shutil.rmtree, proyecto_path, ignore_errors=True)
    background_tasks.add_task(os.remove, zip_path)

    return FileResponse(zip_path, media_type="application/zip", filename="angular_proyecto.zip", background=background_tasks)
