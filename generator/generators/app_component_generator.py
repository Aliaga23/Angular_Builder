import json

def generate_app_component_files(flat_components, background_color="#121212"):
    hierarchical_components = organize_components_by_hierarchy(flat_components)

    return {
        "src/app/app.component.ts": generate_app_ts(),
        "src/app/app.component.html": generate_app_html(hierarchical_components),
        "src/app/app.component.scss": generate_app_scss(hierarchical_components, background_color),
    }


def generate_app_ts():
    return """import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent { }
"""


def generate_app_html(components):
    # Si hay páginas, usamos router-outlet directamente
    if not components:  # vacío o []
        return '<div class="app-container">\n  <router-outlet></router-outlet>\n</div>'

    html = '<div class="app-container">\n'

    def dict_to_angular_props(props: dict) -> str:
        def format_value(val):
            if isinstance(val, str):
                return f"'{val}'"
            elif isinstance(val, bool):
                return 'true' if val else 'false'
            elif isinstance(val, (int, float)):
                return str(val)
            elif isinstance(val, list):
                return '[' + ', '.join(format_value(v) for v in val) + ']'
            elif isinstance(val, dict):
                return '{' + ', '.join(f"'{k}': {format_value(v)}" for k, v in val.items()) + '}'
            else:
                return 'null'
        return '{' + ', '.join(f"'{k}': {format_value(v)}" for k, v in props.items()) + '}'

    def render_component(component, indent=2):
        spaces = " " * indent
        props_str = dict_to_angular_props(component.props)
        html_line = f'{spaces}<app-{component.type} id="{component.id}" class="positioned-component" [props]="{props_str}"'
        html_lines = []

        if component.children:
            html_lines.append(html_line + ">")
            for child in component.children:
                html_lines.append(render_component(child, indent + 2))
            html_lines.append(f"{spaces}</app-{component.type}>")
        else:
            html_lines.append(html_line + f"></app-{component.type}>")

        return "\n".join(html_lines)

    for c in components:
        html += render_component(c) + "\n"

    html += "</div>"
    return html


def generate_app_scss(components, background_color="#121212"):
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

    def render_style(c):
        block = f"""#{c.id} {{
  left: {c.position.x}px;
  top: {c.position.y}px;
  width: {c.size.width}px;
  height: {c.size.height}px;"""
        if c.zIndex is not None:
            block += f"\n  z-index: {c.zIndex};"
        block += "\n}\n"
        return block

    def traverse(components):
        styles = ""
        for c in components:
            styles += render_style(c)
            if hasattr(c, "children") and c.children:
                styles += traverse(c.children)
        return styles

    scss += traverse(components)
    return scss


# ✅ Nueva función para organizar por jerarquía
def organize_components_by_hierarchy(components):
    components_map = {c.id: c for c in components}
    for c in components:
        c.children = []

    roots = []

    for component in components:
        if component.parentId and component.parentId in components_map:
            parent = components_map[component.parentId]
            parent.children.append(component)
        else:
            roots.append(component)

    def sort_fn(c): return c.zIndex if c.zIndex is not None else c.position.y
    return sorted(roots, key=sort_fn)
