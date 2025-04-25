# crud-generator/utils.py

def map_data_type(xmi_type: str) -> str:
    mapping = {
        "int": "number", "integer": "number", "long": "number",
        "float": "number", "double": "number", "decimal": "number",
        "char": "string", "varchar": "string", "text": "string",
        "bool": "boolean", "boolean": "boolean",
        "date": "Date", "datetime": "Date", "timestamp": "Date", "time": "Date",
    }
    return mapping.get(xmi_type.lower(), xmi_type)
