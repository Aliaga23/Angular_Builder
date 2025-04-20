def to_pascal_case(s: str) -> str:
    """
    Convierte un string tipo kebab-case o snake_case a PascalCase.
    Ejemplo: 'input-field' -> 'InputField'
    """
    return ''.join(word.capitalize() for word in s.replace('_', '-').split('-'))


def to_camel_case(s: str) -> str:
    """
    Convierte un string tipo kebab-case a camelCase.
    Ejemplo: 'input-field' -> 'inputField'
    """
    parts = s.replace('_', '-').split('-')
    return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])


def sanitize_identifier(s: str) -> str:
    """
    Reemplaza caracteres no válidos para identificadores de Angular.
    """
    return ''.join(c if c.isalnum() else '_' for c in s)
