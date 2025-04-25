from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from crud_generator.schemas import GenerateRequest
from crud_generator.build_crud_project import build_crud_project
import traceback
from fastapi import Request

router = APIRouter()

@router.post("/generar-crud/")
async def generar_crud_endpoint(request: GenerateRequest):
    try:
        zip_path = build_crud_project(request)
        return FileResponse(
            path=zip_path,
            filename=f"{request.name.lower()}-crud.zip",
            media_type="application/zip"
        )
    except Exception as e:
        print("[❌ ERROR] Excepción al generar proyecto CRUD:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))