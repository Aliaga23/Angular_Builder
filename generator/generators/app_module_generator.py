from generator.utils import to_pascal_case

def generate_app_module_file(pages):
    all_components = []
    for page in pages:
        all_components.extend(page.components)

    unique_types = set()

    def collect(component):
        tipo = getattr(component, "type", None)
        children = getattr(component, "children", [])

        if tipo:
            unique_types.add(tipo)

        for child in children:
            collect(child)

    for component in all_components:
        collect(component)

    imports = [
        "import { NgModule } from '@angular/core';",
        "import { BrowserModule } from '@angular/platform-browser';",
        "import { FormsModule } from '@angular/forms';",
        "import { AppComponent } from './app.component';",
        "import { AppRoutingModule } from './app-routing.module';"
    ]

    declarations = ["AppComponent"]

    for comp_type in sorted(unique_types):
        class_name = to_pascal_case(comp_type) + "Component"
        path = f"./components/{comp_type}/{comp_type}.component"
        imports.append(f"import {{ {class_name} }} from '{path}';")
        declarations.append(class_name)

    for page in pages:
        page_class = to_pascal_case(page.name) + "Component"
        page_path = f"./pages/{page.name}/{page.name}.component"
        imports.append(f"import {{ {page_class} }} from '{page_path}';")
        declarations.append(page_class)

    content = "\n".join(imports) + f"""

@NgModule({{
  declarations: [{", ".join(declarations)}],
  imports: [BrowserModule, FormsModule, AppRoutingModule],
  providers: [],
  bootstrap: [AppComponent]
}})
export class AppModule {{ }}
"""

    return {"src/app/app.module.ts": content}
