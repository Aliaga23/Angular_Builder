from generator.utils import to_pascal_case

def generate_routing_files(pages, default_page: str):
    imports = ""
    routes = ""

    for page in pages:
        class_name = to_pascal_case(page.name) + "Component"
        imports += f"import {{ {class_name} }} from './pages/{page.name}/{page.name}.component';\n"

        path = "" if page.name == default_page else page.name
        routes += f"  {{ path: '{path}', component: {class_name} }},\n"

    return {
        "src/app/app-routing.module.ts": f"""import {{ NgModule }} from '@angular/core';
import {{ RouterModule, Routes }} from '@angular/router';
{imports.strip()}

const routes: Routes = [
{routes.strip()}
];

@NgModule({{
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
}})
export class AppRoutingModule {{ }}
"""
    }
