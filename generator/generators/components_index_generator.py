def generate_components_index_file(components):
    unique_types = set()

    def collect(component):
        tipo = getattr(component, "type", None)
        children = getattr(component, "children", [])

        if tipo:
            unique_types.add(tipo)

        for child in children:
            collect(child)

    for component in components:
        collect(component)

    lines = ["// Índice generado automáticamente"]
    for t in sorted(unique_types):
        lines.append(f"export * from './{t}/{t}.component';")

    return {
        "src/app/components/index.ts": "\n".join(lines)
    }
