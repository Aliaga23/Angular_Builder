from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse, JSONResponse
from crud_generator.schemas import GenerateRequest
from crud_generator.build_crud_project import build_crud_project
import traceback
import xml.etree.ElementTree as ET

router = APIRouter()


def normalize_type(value: str) -> str:
    value = value.lower()
    if value in ["int", "integer"]:
        return "integer"
    elif value in ["float", "double", "decimal"]:
        return "float"
    elif value in ["bool", "boolean"]:
        return "boolean"
    elif value in ["string", "str", "char"]:
        return "string"
    else:
        return "string"

def parse_ea_xmi(content: str):
    ns = {"UML": "omg.org/UML1.3"}
    root = ET.fromstring(content)
    classes = []

    for class_elem in root.findall(".//UML:Class", ns):
        class_name = class_elem.attrib.get("name", "UnnamedClass")
        if class_name == "EARootClass":
            continue

        attributes = []

        classifier = class_elem.find("UML:Classifier.feature", ns)
        if classifier is not None:
            for attr in classifier.findall("UML:Attribute", ns):
                attr_name = attr.attrib.get("name", "unnamed")
                tagged = attr.find("UML:ModelElement.taggedValue", ns)
                attr_type = "string"
                is_required = True
                if tagged is not None:
                    for tag in tagged.findall("UML:TaggedValue", ns):
                        if tag.attrib.get("tag") == "type":
                            attr_type = normalize_type(tag.attrib.get("value", "string"))
                        elif tag.attrib.get("tag") == "lowerBound":
                            is_required = tag.attrib.get("value", "1") != "0"

                attributes.append({
                    "name": attr_name,
                    "type": attr_type,
                    "isRequired": is_required
                })

        classes.append({
            "name": class_name,
            "attributes": attributes,
            "primary_key": {},
            "auto_increment": False
        })

    return classes


@router.post("/parse-xmi/")
async def parse_xmi_endpoint(file: UploadFile = File(...)):
    try:
        content = await file.read()
        decoded = content.decode("windows-1252")
        result = parse_ea_xmi(decoded)
        return JSONResponse(content=result)
    except Exception as e:
        print("[❌ ERROR] Falló el parseo del XMI:")
        traceback.print_exc()
        return JSONResponse(status_code=400, content={"error": str(e)})


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
