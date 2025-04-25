from crud_generator.builder import *
from crud_generator.schemas import GenerateRequest
from crud_generator.zip_generator import create_zip_from_dict

def build_crud_project(request: GenerateRequest) -> str:
    class_name = request.name
    lower_name = class_name.lower()

    files = {
        "src/index.html": generate_index_html(class_name),
        "src/styles.scss": generate_global_styles(),
        "src/main.ts": generate_main_ts(),
        "angular.json": generate_angular_json(lower_name),
        "package.json": generate_package_json(lower_name),
        "tsconfig.json": generate_tsconfig(),
        "tsconfig.app.json": generate_tsconfig_app(),
        "tsconfig.spec.json": generate_tsconfig_spec(),
        "README.md": generate_readme(class_name),

        f"src/app/models/{lower_name}.model.ts": generate_model(request),
        f"src/app/services/{lower_name}.service.ts": generate_service(request),

        f"src/app/components/{lower_name}-list/{lower_name}-list.component.ts": generate_list_component_ts(request),
        f"src/app/components/{lower_name}-list/{lower_name}-list.component.html": generate_list_component_html(request),
        f"src/app/components/{lower_name}-list/{lower_name}-list.component.scss": generate_list_component_scss(),

        f"src/app/components/{lower_name}-detail/{lower_name}-detail.component.ts": generate_detail_component_ts(request),
        f"src/app/components/{lower_name}-detail/{lower_name}-detail.component.html": generate_detail_component_html(request),
        f"src/app/components/{lower_name}-detail/{lower_name}-detail.component.scss": generate_detail_component_scss(),

        f"src/app/components/{lower_name}-form/{lower_name}-form.component.ts": generate_form_component_ts(request),
        f"src/app/components/{lower_name}-form/{lower_name}-form.component.html": generate_form_component_html(request),
        f"src/app/components/{lower_name}-form/{lower_name}-form.component.scss": generate_form_component_scss(),

        f"src/app/components/navbar/navbar.component.ts": generate_navbar_component_ts(class_name),
        f"src/app/components/navbar/navbar.component.html": generate_navbar_component_html(class_name, lower_name),
        f"src/app/components/navbar/navbar.component.scss": generate_navbar_component_scss(),

        f"src/app/app.module.ts": generate_app_module(request),
        f"src/app/app.component.ts": generate_app_component(class_name),
        f"src/app/app.component.html": generate_app_component_html(),
        f"src/app/app.component.scss": generate_app_component_scss(),
    }

    return create_zip_from_dict(files)
