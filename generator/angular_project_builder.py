import os
import shutil
import tempfile
from typing import List
from fastapi import HTTPException

from generator.models import AngularAppSchema, Component
from generator.generators.global_files import generate_global_files
from generator.generators.app_component_generator import generate_app_component_files
from generator.generators.component_generator import generate_component_files
from generator.generators.app_module_generator import generate_app_module_file
from generator.generators.components_index_generator import generate_components_index_file
from generator.generators.page_generator import generate_pages_files
from generator.generators.routing_generator import generate_routing_files


def agregar_bat_inicio(ruta_proyecto: str):
    bat_path = os.path.join(ruta_proyecto, "start-angular.bat")
    with open(bat_path, "w") as f:
        f.write("npm install\nnpx ng serve\npause")

def generar_proyecto_angular(data: AngularAppSchema) -> str:
    try:
        temp_dir = tempfile.mkdtemp()

        app_name = data.appName
        background_color = data.backgroundColor
        default_page = data.defaultPage
        all_components = []

        for page in data.pages:
            all_components.extend(page.components)

        files = {
            **generate_global_files(app_name),
            **generate_app_component_files([], background_color),
            **generate_component_files(all_components, background_color),
            **generate_app_module_file(data.pages),
            **generate_components_index_file(all_components),
            **generate_pages_files(data.pages, background_color),
            **generate_routing_files(data.pages, default_page),
        }

        # Escribir todos los archivos generados
        for path, content in files.items():
            full_path = os.path.join(temp_dir, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

        agregar_bat_inicio(temp_dir)

        # Comprimir
        zip_path = shutil.make_archive(temp_dir, "zip", temp_dir)
        return zip_path

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el proyecto: {str(e)}")


def organize_components_by_hierarchy(components: List[Component]):
    components_map = {c.id: {**c.dict(), "children": []} for c in components}
    roots = []

    for component in components:
        if component.parentId and component.parentId in components_map:
            components_map[component.parentId]["children"].append(components_map[component.id])
        else:
            roots.append(components_map[component.id])

    def sort_fn(c):
        return c.get("zIndex") or c["position"]["y"]

    return sorted(roots, key=sort_fn)
