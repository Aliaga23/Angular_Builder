import os
import zipfile
import tempfile
from typing import Dict

def create_zip_from_dict(files: Dict[str, str], base_dir: str = None) -> str:
    """
    Crea un archivo ZIP a partir de un diccionario de archivos.

    :param files: Diccionario con claves como rutas relativas y valores como contenido.
    :param base_dir: Carpeta base donde se generará el proyecto (si no se proporciona, se usará una temporal).
    :return: Ruta al archivo ZIP generado.
    """
    base_dir = base_dir or tempfile.mkdtemp()

    # Crear archivos reales en el filesystem
    for rel_path, content in files.items():
        full_path = os.path.join(base_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    # Crear archivo ZIP
    zip_path = os.path.join(tempfile.gettempdir(), f"crud_project_{next(tempfile._get_candidate_names())}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, filenames in os.walk(base_dir):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                arcname = os.path.relpath(filepath, base_dir)
                zipf.write(filepath, arcname)

    return zip_path
