from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from crud_generator.schemas import GenerateRequest
from crud_generator.build_crud_project import build_crud_project
import traceback
import xml.etree.ElementTree as ET

router = APIRouter()

XMI_NS = "http://schema.omg.org/spec/XMI/2.1"
UML_21_NS = "http://schema.omg.org/spec/UML/2.1"
UML_13_NS = "omg.org/UML1.3"

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

def parse_uml13(root):
    ns = {"UML": UML_13_NS}
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
                attr_type = "string"
                is_required = True

                tagged = attr.find("UML:ModelElement.taggedValue", ns)
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

def parse_uml21(root):
    classes = []

    for elem in root.iter():
        if elem.tag.endswith("packagedElement") and elem.attrib.get(f"{{{XMI_NS}}}type") == "uml:Class":
            class_name = elem.attrib.get("name", "UnnamedClass")
            attributes = []

            for attr in elem.findall("ownedAttribute"):
                attr_name = attr.attrib.get("name", "unnamed")
                type_name = "string"
                type_elem = attr.find("type")
                if type_elem is not None:
                    ref = type_elem.attrib.get(f"{{{XMI_NS}}}idref", "")
                    type_name = normalize_type(ref)

                lower_val = attr.find("lowerValue")
                is_required = lower_val is None or lower_val.attrib.get("value", "1") != "0"

                attributes.append({
                    "name": attr_name,
                    "type": type_name,
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
        root = ET.fromstring(decoded)

        if UML_13_NS in decoded:
            result = parse_uml13(root)
        elif UML_21_NS in decoded or "uml:Model" in decoded:
            result = parse_uml21(root)
        else:
            raise Exception("No se reconoce la versión UML compatible (1.3 o 2.x)")

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
