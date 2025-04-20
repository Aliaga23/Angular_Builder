import json

def generate_pages_files(pages, background_color):
    files = {}
    for page in pages:
        name = page.name
        class_name = name.capitalize() + "Component"
        components = organize_components_by_hierarchy(page.components)

        files[f"src/app/pages/{name}/{name}.component.ts"] = _generate_page_ts(name)
        files[f"src/app/pages/{name}/{name}.component.html"] = _generate_page_html(components)
        files[f"src/app/pages/{name}/{name}.component.scss"] = _generate_page_scss(components, background_color)

    return files


from generator.utils import to_pascal_case

def _generate_page_ts(name: str):
    class_name = to_pascal_case(name) + "Component"
    return f"""import {{ Component }} from '@angular/core';

@Component({{
  selector: 'app-{name}',
  templateUrl: './{name}.component.html',
  styleUrls: ['./{name}.component.scss']
}})
export class {class_name} {{}}
"""



def _generate_page_html(components: list):
    html = '<div class="app-container">\n'

    def render_component(c, indent=2):
        spaces = " " * indent
        props_str = json.dumps(c.props).replace('"', "'")
        html_line = f'{spaces}<app-{c.type} id="{c.id}" class="positioned-component" [props]="{props_str}">'
        html_lines = [html_line]

        if getattr(c, "children", []):
            for child in c.children:
                html_lines.append(render_component(child, indent + 2))
            html_lines.append(f"{spaces}</app-{c.type}>")
        else:
            html_lines[-1] += f"</app-{c.type}>"

        return "\n".join(html_lines)

    for c in components:
        html += render_component(c) + "\n"

    html += "</div>"
    return html


def _generate_page_scss(components, background_color: str):
    scss = f"""@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@300;400;500&display=swap');

.app-container {{
  position: relative;
  width: 100%;
  height: 100vh;
  background-color: {background_color};
  font-family: 'Oswald', sans-serif;
}}

.positioned-component {{
  position: absolute;
  box-sizing: border-box;
}}\n"""

    def add_style_block(c):
        block = f"""#{c.id} {{
  left: {c.position.x}px;
  top: {c.position.y}px;
  width: {c.size.width}px;
  height: {c.size.height}px;"""
        if c.zIndex is not None:
            block += f"\n  z-index: {c.zIndex};"
        block += "\n}\n"
        return block

    def traverse_and_generate_styles(components):
        result = ""
        for c in components:
            result += add_style_block(c)
            if getattr(c, "children", []):
                result += traverse_and_generate_styles(c.children)
        return result

    scss += traverse_and_generate_styles(components)
    return scss


def organize_components_by_hierarchy(components):
    component_map = {c.id: c for c in components}
    for c in components:
        c.children = []

    for c in components:
        if c.parentId and c.parentId in component_map:
            component_map[c.parentId].children.append(c)

    roots = [c for c in components if not c.parentId]
    return sorted(roots, key=lambda c: c.zIndex if c.zIndex is not None else c.position.y)
