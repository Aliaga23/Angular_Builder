# crud-generator/builder.py

from crud_generator.schemas import GenerateRequest
from crud_generator.utils import map_data_type

def generate_model(request: GenerateRequest) -> str:
    lines = []
    class_name = request.name
    pk_name = request.primary_key.name
    pk_type = map_data_type(request.primary_key.type)
    attributes = request.attributes

    has_pk = any(attr.name == pk_name for attr in attributes)
    lines.append(f"export interface {class_name} {{")

    if not has_pk:
        lines.append(f"  {pk_name}: {pk_type};")

    for attr in attributes:
        if attr.name == pk_name and not has_pk:
            continue
        ts_type = map_data_type(attr.type)
        nullable = " | null" if attr.isRequired is False else ""
        lines.append(f"  {attr.name}: {ts_type}{nullable};")

    lines.append("}")
    return "\n".join(lines)



def generate_service(request: GenerateRequest) -> str:
    class_name = request.name
    lower_name = class_name.lower()
    pk_name = request.primary_key.name
    ts_type = map_data_type(request.primary_key.type)
    capitalized_pk = pk_name[0].upper() + pk_name[1:]
    auto_increment = request.auto_increment

    create_type = f"Omit<{class_name}, '{pk_name}'>" if auto_increment else class_name
    increment_line = (
        f"this.next{capitalized_pk}++" if ts_type == "number"
        else f"String(this.next{capitalized_pk}++)"
    ) if auto_increment else None

    lines = [
        f"import {{ Injectable }} from '@angular/core';",
        f"import {{ Observable, of }} from 'rxjs';",
        f"import {{ {class_name} }} from '../models/{lower_name}.model';",
        "",
        "@Injectable({ providedIn: 'root' })",
        f"export class {class_name}Service {{",
        f"  private items: {class_name}[] = [];",
    ]

    if auto_increment:
        lines.append(f"  private next{capitalized_pk} = 1;")

    lines += [
        "",
        "  constructor() { }",
        "",
        f"  getAll(): Observable<{class_name}[]> {{ return of(this.items); }}",
        "",
        f"  getById({pk_name}: {ts_type}): Observable<{class_name}> {{",
        f"    const item = this.items.find(item => String(item.{pk_name}) === String({pk_name}));",
        f"    return of(item as {class_name});",
        "  }",
        "",
        f"  create(item: {create_type}): Observable<{class_name}> {{"
    ]

    if auto_increment:
        lines += [
            f"    const newItem = {{",
            f"      ...item,",
            f"      {pk_name}: {increment_line}",
            f"    }} as {class_name};"
        ]
    else:
        lines += [
            f"    const exists = this.items.some(i => String(i.{pk_name}) === String(item.{pk_name}));",
            f"    if (exists) throw new Error('{pk_name} duplicado');",
            f"    const newItem = {{ ...item }} as {class_name};"
        ]

    lines += [
        "    this.items.push(newItem);",
        "    return of(newItem);",
        "  }",
        "",
        f"  update(item: {class_name}): Observable<{class_name}> {{",
        f"    const index = this.items.findIndex(i => String(i.{pk_name}) === String(item.{pk_name}));",
        "    if (index !== -1) { this.items[index] = item; return of(item); }",
        f"    return of({{}} as {class_name});",
        "  }",
        "",
        f"  delete({pk_name}: {ts_type}): Observable<boolean> {{",
        f"    const index = this.items.findIndex(item => String(item.{pk_name}) === String({pk_name}));",
        "    if (index !== -1) { this.items.splice(index, 1); return of(true); }",
        "    return of(false);",
        "  }",
        "}"
    ]

    return "\n".join(lines)




def generate_app_module(request: GenerateRequest) -> str:
    class_name = request.name
    lower_name = class_name.lower()

    return f"""import {{ NgModule }} from '@angular/core';
import {{ BrowserModule }} from '@angular/platform-browser';
import {{ FormsModule, ReactiveFormsModule }} from '@angular/forms';
import {{ HttpClientModule }} from '@angular/common/http';
import {{ RouterModule }} from '@angular/router';

import {{ AppComponent }} from './app.component';
import {{ {class_name}ListComponent }} from './components/{lower_name}-list/{lower_name}-list.component';
import {{ {class_name}DetailComponent }} from './components/{lower_name}-detail/{lower_name}-detail.component';
import {{ {class_name}FormComponent }} from './components/{lower_name}-form/{lower_name}-form.component';
import {{ NavbarComponent }} from './components/navbar/navbar.component';

@NgModule({{
  declarations: [
    AppComponent,
    {class_name}ListComponent,
    {class_name}DetailComponent,
    {class_name}FormComponent,
    NavbarComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    RouterModule.forRoot([
      {{ path: '', redirectTo: '{lower_name}s', pathMatch: 'full' }},
      {{ path: '{lower_name}s', component: {class_name}ListComponent }},
      {{ path: '{lower_name}s/new', component: {class_name}FormComponent }},
      {{ path: '{lower_name}s/:id', component: {class_name}DetailComponent }},
      {{ path: '{lower_name}s/:id/edit', component: {class_name}FormComponent }},
      {{ path: '**', redirectTo: '{lower_name}s' }}
    ])
  ],
  providers: [],
  bootstrap: [AppComponent]
}})
export class AppModule {{ }}
"""


def generate_app_component(class_name: str) -> str:
    return f"""import {{ Component }} from '@angular/core';

@Component({{
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
}})
export class AppComponent {{
  title = '{class_name} CRUD';
}}
"""
def generate_app_component_html() -> str:
    return """<app-navbar></app-navbar>
<div class="container">
  <router-outlet></router-outlet>
</div>"""
def generate_app_component_scss() -> str:
    return """.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}"""
def generate_navbar_component_ts(class_name: str) -> str:
    return f"""import {{ Component }} from '@angular/core';

@Component({{
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
}})
export class NavbarComponent {{
  title = '{class_name} CRUD';
}}
"""
def generate_navbar_component_html(class_name: str, lower_class_name: str) -> str:
    return f"""<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container">
    <a class="navbar-brand" routerLink="/">{{{{ title }}}}</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
            aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item">
          <a class="nav-link" routerLink="/{lower_class_name}s" routerLinkActive="active">
            <i class="bi bi-list me-1"></i> Lista
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" routerLink="/{lower_class_name}s/new" routerLinkActive="active">
            <i class="bi bi-plus-circle me-1"></i> Nuevo
          </a>
        </li>
      </ul>
    </div>
  </div>
</nav>"""
def generate_navbar_component_scss() -> str:
    return """.navbar {
  background-color: #1a2234 !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
  font-weight: 600;
}

.nav-link {
  color: #94a3b8 !important;
  transition: color 0.2s;
  padding: 0.5rem 1rem;
}

.nav-link:hover {
  color: #ffffff !important;
}

.nav-link.active {
  color: #3f51b5 !important;
  font-weight: 500;
  position: relative;
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0.5rem;
  right: 0.5rem;
  height: 2px;
  background-color: #3f51b5;
}"""

def generate_index_html(class_name: str) -> str:
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>{class_name} CRUD</title>
  <base href="/">

  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@200;300;400;500;600;700&display=swap" rel="stylesheet">

  <!-- Bootstrap CSS -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <!-- Bootstrap Icons -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</head>
<body class="bg-dark text-light">
  <app-root></app-root>

  <!-- Bootstrap JS Bundle with Popper -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

def generate_global_styles() -> str:
    return """/* Estilos globales */
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@200;300;400;500;600;700&display=swap');

:root {
  --bs-primary: #3f51b5;
  --bs-secondary: #64748b;
  --bs-success: #10b981;
  --bs-info: #3b82f6;
  --bs-warning: #f59e0b;
  --bs-danger: #ef4444;
}

body {
  font-family: 'Oswald', sans-serif;
  background-color: #121212;
  color: #f8fafc;
}

.card {
  background-color: #1e293b;
  border: none;
  border-radius: 0.5rem;
}

.table {
  color: #e2e8f0;
}

.form-control, .form-select {
  background-color: #263548;
  border-color: #334155;
  color: #f8fafc;
}

.form-control:focus, .form-select:focus {
  background-color: #263548;
  border-color: #3f51b5;
  box-shadow: 0 0 0 0.25rem rgba(63, 81, 181, 0.25);
  color: #f8fafc;
}

.alert-danger {
  background-color: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.badge {
  font-weight: 500;
}

.table-striped > tbody > tr:nth-of-type(odd) {
  background-color: rgba(255, 255, 255, 0.05);
}

.table-hover tbody tr:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
"""
def generate_main_ts() -> str:
    return """import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));"""

def generate_angular_json(app_name: str) -> str:
    return f'''{{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {{
    "{app_name}-crud": {{
      "projectType": "application",
      "schematics": {{
        "@schematics/angular:component": {{
          "style": "scss"
        }}
      }},
      "root": "",
      "sourceRoot": "src",
      "prefix": "app",
      "architect": {{
        "build": {{
          "builder": "@angular-devkit/build-angular:browser",
          "options": {{
            "outputPath": "dist/{app_name}-crud",
            "index": "src/index.html",
            "main": "src/main.ts",
            "polyfills": ["zone.js"],
            "tsConfig": "tsconfig.app.json",
            "inlineStyleLanguage": "scss",
            "assets": ["src/favicon.ico", "src/assets"],
            "styles": ["src/styles.scss"],
            "scripts": []
          }},
          "configurations": {{
            "production": {{
              "outputHashing": "all"
            }},
            "development": {{
              "buildOptimizer": false,
              "optimization": false,
              "vendorChunk": true,
              "extractLicenses": false,
              "sourceMap": true,
              "namedChunks": true
            }}
          }},
          "defaultConfiguration": "production"
        }},
        "serve": {{
          "builder": "@angular-devkit/build-angular:dev-server",
          "configurations": {{
            "production": {{
              "browserTarget": "{app_name}-crud:build:production"
            }},
            "development": {{
              "browserTarget": "{app_name}-crud:build:development"
            }}
          }},
          "defaultConfiguration": "development"
        }},
        "extract-i18n": {{
          "builder": "@angular-devkit/build-angular:extract-i18n",
          "options": {{
            "browserTarget": "{app_name}-crud:build"
          }}
        }},
        "test": {{
          "builder": "@angular-devkit/build-angular:karma",
          "options": {{
            "polyfills": ["zone.js", "zone.js/testing"],
            "tsConfig": "tsconfig.spec.json",
            "inlineStyleLanguage": "scss",
            "assets": ["src/favicon.ico", "src/assets"],
            "styles": ["src/styles.scss"],
            "scripts": []
          }}
        }}
      }}
    }}
  }},
  "defaultProject": "{app_name}-crud"
}}'''



def generate_package_json(app_name: str) -> str:
    return f'''{{
  "name": "{app_name}-crud",
  "version": "0.1.0",
  "scripts": {{
    "ng": "ng",
    "start": "ng serve",
    "build": "ng build",
    "watch": "ng build --watch --configuration development",
    "test": "ng test"
  }},
  "private": true,
  "dependencies": {{
    "@angular/animations": "^16.2.0",
    "@angular/common": "^16.2.0",
    "@angular/compiler": "^16.2.0",
    "@angular/core": "^16.2.0",
    "@angular/forms": "^16.2.0",
    "@angular/platform-browser": "^16.2.0",
    "@angular/platform-browser-dynamic": "^16.2.0",
    "@angular/router": "^16.2.0",
    "rxjs": "~7.8.0",
    "tslib": "^2.3.0",
    "zone.js": "~0.13.0"
  }},
  "devDependencies": {{
    "@angular-devkit/build-angular": "^16.2.0",
    "@angular/cli": "~16.2.0",
    "@angular/compiler-cli": "^16.2.0",
    "@types/jasmine": "~4.3.0",
    "jasmine-core": "~4.6.0",
    "karma": "~6.4.0",
    "karma-chrome-launcher": "~3.2.0",
    "karma-coverage": "~2.2.0",
    "karma-jasmine": "~5.1.0",
    "karma-jasmine-html-reporter": "~2.1.0",
    "typescript": "~5.1.3"
  }}
}}'''


def generate_tsconfig() -> str:
    return """{
  "compileOnSave": false,
  "compilerOptions": {
    "baseUrl": "./",
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": false,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "sourceMap": true,
    "declaration": false,
    "downlevelIteration": true,
    "experimentalDecorators": true,
    "moduleResolution": "node",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": ["ES2022", "dom"]
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}"""
def generate_tsconfig_app() -> str:
    return """{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/app",
    "types": []
  },
  "files": [
    "src/main.ts"
  ],
  "include": [
    "src/**/*.d.ts"
  ]
}"""
def generate_tsconfig_spec() -> str:
    return """{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/spec",
    "types": ["jasmine"]
  },
  "include": [
    "src/**/*.spec.ts",
    "src/**/*.d.ts"
  ]
}"""


def generate_readme(class_name: str) -> str:
    return f"""# {class_name} CRUD Application

Esta aplicación proporciona una interfaz CRUD completa para gestionar entidades **{class_name}**.

## Características

- Lista de {class_name}s con opciones de filtrado
- Vista detallada de cada {class_name}
- Formulario para crear y editar registros
- Eliminación de registros
- Estilo moderno con Bootstrap 5 y modo oscuro

## Instalación

```bash
npm install 
```
"""
def generate_list_component_ts(request: GenerateRequest) -> str:
    class_name = request.name
    lower_class_name = class_name.lower()
    primary_key = request.primary_key.name

    return f"""import {{ Component, OnInit }} from '@angular/core';
import {{ {class_name} }} from '../../models/{lower_class_name}.model';
import {{ {class_name}Service }} from '../../services/{lower_class_name}.service';

@Component({{
  selector: 'app-{lower_class_name}-list',
  templateUrl: './{lower_class_name}-list.component.html',
  styleUrls: ['./{lower_class_name}-list.component.scss']
}})
export class {class_name}ListComponent implements OnInit {{
  items: {class_name}[] = [];
  loading = true;
  error = '';

  constructor(private {lower_class_name}Service: {class_name}Service) {{ }}

  ngOnInit(): void {{
    this.loadItems();
  }}

  loadItems(): void {{
    this.loading = true;
    this.{lower_class_name}Service.getAll().subscribe({{
      next: (data) => {{
        this.items = data;
        this.loading = false;
      }},
      error: (err) => {{
        this.error = 'Error al cargar los datos';
        this.loading = false;
        console.error(err);
      }}
    }});
  }}

  deleteItem({primary_key}: any): void {{
    if (confirm('¿Estás seguro de que deseas eliminar este elemento?')) {{
      this.{lower_class_name}Service.delete({primary_key}).subscribe({{
        next: (success) => {{
          if (success) {{
            this.items = this.items.filter(item => item.{primary_key} !== {primary_key});
          }}
        }},
        error: (err) => {{
          console.error('Error al eliminar:', err);
        }}
      }});
    }}
  }}
}}"""


def generate_list_component_html(request: GenerateRequest) -> str:
    class_name = request.name
    lower_class_name = class_name.lower()
    primary_key = request.primary_key.name
    attributes = request.attributes

    ths = f"                <th>{primary_key.capitalize()}</th>\n"
    tds = f"                <td>{{{{ item.{primary_key} }}}}</td>\n"

    for attr in attributes:
        if attr.name == primary_key:
            continue
        ths += f"                <th>{attr.name.capitalize()}</th>\n"

        if attr.type.lower() == "boolean":
            tds += f"""                <td>
                  <span class="badge bg-{{{{ item.{attr.name} ? 'success' : 'secondary' }}}}">
                    {{{{ item.{attr.name} ? 'Sí' : 'No' }}}}
                  </span>
                </td>\n"""
        elif attr.type.lower() in ["date", "datetime"]:
            tds += f"                <td>{{{{ item.{attr.name} | date:'short' }}}}</td>\n"
        else:
            tds += f"                <td>{{{{ item.{attr.name} }}}}</td>\n"

    return f"""<div class="container mt-4">
  <div class="row mb-4">
    <div class="col-md-8">
      <h1>{class_name}s</h1>
    </div>
    <div class="col-md-4 text-md-end">
      <a [routerLink]="['/{lower_class_name}s/new']" class="btn btn-primary">
        <i class="bi bi-plus-circle me-1"></i> Nuevo {class_name}
      </a>
    </div>
  </div>

  <div class="card shadow-sm">
    <div class="card-body">
      <div *ngIf="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Cargando...</span>
        </div>
        <p class="mt-2">Cargando...</p>
      </div>

      <div *ngIf="error" class="alert alert-danger">
        {{{{ error }}}}
      </div>

      <div *ngIf="!loading && !error">
        <div *ngIf="items.length === 0" class="text-center py-5">
          <p class="mb-3">No hay {lower_class_name}s disponibles.</p>
          <a [routerLink]="['/{lower_class_name}s/new']" class="btn btn-primary">
            Crear el primero
          </a>
        </div>

        <div class="table-responsive" *ngIf="items.length > 0">
          <table class="table table-striped table-hover">
            <thead>
              <tr>
{ths}                <th class="text-end">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let item of items">
{tds}                <td class="text-end">
                  <div class="btn-group btn-group-sm">
                    <a [routerLink]="['/{lower_class_name}s', item.{primary_key}]" class="btn btn-info">
                      <i class="bi bi-eye"></i>
                    </a>
                    <a [routerLink]="['/{lower_class_name}s', item.{primary_key}, 'edit']" class="btn btn-warning">
                      <i class="bi bi-pencil"></i>
                    </a>
                    <button (click)="deleteItem(item.{primary_key})" class="btn btn-danger">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>"""




def generate_list_component_scss() -> str:
    return """.card {
  background-color: #1e293b;
  border: none;
  border-radius: 0.5rem;
}

.table {
  color: white; /* <-- esto cambia los textos */
  margin-bottom: 0;
}

.table th {
  color: white;
}

.table td {
  color: white;
}

.table-striped > tbody > tr:nth-of-type(odd) {
  background-color: rgba(255, 255, 255, 0.05);
}

.table-hover tbody tr:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.btn-group {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}
"""

def generate_detail_component_ts(request: GenerateRequest) -> str:
    class_name = request.name
    lower_class_name = class_name.lower()
    primary_key = request.primary_key.name

    return f"""import {{ Component, OnInit }} from '@angular/core';
import {{ ActivatedRoute, Router }} from '@angular/router';
import {{ {class_name} }} from '../../models/{lower_class_name}.model';
import {{ {class_name}Service }} from '../../services/{lower_class_name}.service';

@Component({{
  selector: 'app-{lower_class_name}-detail',
  templateUrl: './{lower_class_name}-detail.component.html',
  styleUrls: ['./{lower_class_name}-detail.component.scss']
}})
export class {class_name}DetailComponent implements OnInit {{
  item: {class_name} | null = null;
  loading = true;
  error = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private {lower_class_name}Service: {class_name}Service
  ) {{ }}

  ngOnInit(): void {{
    this.loadItem();
  }}

  loadItem(): void {{
    const id = +this.route.snapshot.paramMap.get('id')!;
    if (!id) {{
      this.error = 'ID inválido';
      this.loading = false;
      return;
    }}

    this.{lower_class_name}Service.getById(id).subscribe({{
      next: (data) => {{
        this.item = data;
        this.loading = false;
      }},
      error: (err) => {{
        this.error = 'Error al cargar los datos';
        this.loading = false;
        console.error(err);
      }}
    }});
  }}

  deleteItem(): void {{
    if (!this.item) return;

    if (confirm('¿Estás seguro de que deseas eliminar este elemento?')) {{
      this.{lower_class_name}Service.delete(this.item.{primary_key}).subscribe({{
        next: (success) => {{
          if (success) {{
            this.router.navigate(['/{lower_class_name}s']);
          }}
        }},
        error: (err) => {{
          console.error('Error al eliminar:', err);
        }}
      }});
    }}
  }}
}}"""

def generate_detail_component_html(request: GenerateRequest) -> str:
    class_name = request.name
    lower_class_name = class_name.lower()
    primary_key = request.primary_key.name
    attributes = request.attributes

    rows = f"""<div class="list-group-item d-flex justify-content-between">
  <strong>{primary_key.capitalize()}</strong>
  <span>{{{{ item.{primary_key} }}}}</span>
</div>"""

    for attr in attributes:
        if attr.name == primary_key:
            continue

        if attr.type.lower() == "boolean":
            value = (
                f"""<span class="badge bg-{{{{ item.{attr.name} ? 'success' : 'secondary' }}}}">
  {{{{ item.{attr.name} ? 'Sí' : 'No' }}}}
</span>"""
            )
        elif attr.type.lower() in ["date", "datetime"]:
            value = f"{{{{ item.{attr.name} | date:'medium' }}}}"
        else:
            value = f"{{{{ item.{attr.name} }}}}"

        rows += f"""\n<div class="list-group-item d-flex justify-content-between">
  <strong>{attr.name.capitalize()}</strong>
  <span>{value}</span>
</div>"""

    return f"""<div class="container mt-4">
  <div class="row mb-4">
    <div class="col-md-8">
      <h1>Detalles de {class_name}</h1>
    </div>
    <div class="col-md-4 text-md-end">
      <div class="btn-group">
        <a [routerLink]="['/{lower_class_name}s']" class="btn btn-secondary">
          <i class="bi bi-arrow-left me-1"></i> Volver
        </a>
        <a *ngIf="item" [routerLink]="['/{lower_class_name}s', item.{primary_key}, 'edit']" class="btn btn-warning">
          <i class="bi bi-pencil me-1"></i> Editar
        </a>
        <button *ngIf="item" (click)="deleteItem()" class="btn btn-danger">
          <i class="bi bi-trash me-1"></i> Eliminar
        </button>
      </div>
    </div>
  </div>

  <div class="card shadow-sm">
    <div class="card-body">
      <div *ngIf="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Cargando...</span>
        </div>
        <p class="mt-2">Cargando...</p>
      </div>

      <div *ngIf="error" class="alert alert-danger">
        {{{{ error }}}}
      </div>

      <div *ngIf="!loading && !error && item" class="list-group">
        {rows.strip()}
      </div>
    </div>
  </div>
</div>"""


def generate_detail_component_scss() -> str:
    return """.card {
  background-color: #1e293b;
  border: none;
  border-radius: 0.5rem;
}

.list-group-item {
  background-color: #263548;
  border-color: #334155;
  color: #f8fafc;
  transition: background-color 0.2s;
}

.list-group-item:hover {
  background-color: #334155;
}

.btn-group {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}
"""
def generate_form_component_ts(request: GenerateRequest) -> str:
    class_name = request.name
    lower_class_name = class_name.lower()
    primary_key = request.primary_key.name
    attributes = request.attributes
    auto_increment = request.auto_increment

    form_fields = []
    for attr in attributes:
        if auto_increment and attr.name == primary_key:
            continue
        validators = "[Validators.required]" if attr.isRequired else "[]"
        form_fields.append(f"{attr.name}: [null, {validators}]")

    if not auto_increment and not any(attr.name == primary_key for attr in attributes):
        form_fields.insert(0, f"{primary_key}: [null, [Validators.required]]")

    form_fields_str = ',\n      '.join(form_fields)

    return f"""import {{ Component, OnInit }} from '@angular/core';
import {{ FormBuilder, FormGroup, Validators }} from '@angular/forms';
import {{ ActivatedRoute, Router }} from '@angular/router';
import {{ {class_name} }} from '../../models/{lower_class_name}.model';
import {{ {class_name}Service }} from '../../services/{lower_class_name}.service';

@Component({{
  selector: 'app-{lower_class_name}-form',
  templateUrl: './{lower_class_name}-form.component.html',
  styleUrls: ['./{lower_class_name}-form.component.scss']
}})
export class {class_name}FormComponent implements OnInit {{
  form: FormGroup;
  isEditMode = false;
  itemId: any = null;
  loading = false;
  submitting = false;
  error = '';

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private {lower_class_name}Service: {class_name}Service
  ) {{
    this.form = this.fb.group({{
      {form_fields_str}
    }});
  }}

  ngOnInit(): void {{
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {{
      this.isEditMode = true;
      this.itemId = id;
      this.loadItem(id);
    }}
  }}

  loadItem(id: any): void {{
    this.loading = true;
    this.{lower_class_name}Service.getById(id).subscribe({{
      next: (data) => {{
        this.form.patchValue(data);
        this.loading = false;
      }},
      error: (err) => {{
        this.error = 'Error al cargar los datos';
        this.loading = false;
        console.error(err);
      }}
    }});
  }}

  onSubmit(): void {{
    if (this.form.invalid) {{
      this.form.markAllAsTouched();
      return;
    }}

    this.submitting = true;
    const formData = this.form.value;

    if (this.isEditMode && this.itemId !== null) {{
      const updated = {{ ...formData, {primary_key}: this.itemId }} as {class_name};
      this.{lower_class_name}Service.update(updated).subscribe({{
        next: () => this.router.navigate(['/{lower_class_name}s']),
        error: (err) => {{
          this.error = 'Error al actualizar';
          this.submitting = false;
          console.error(err);
        }}
      }});
    }} else {{
      this.{lower_class_name}Service.create(formData).subscribe({{
        next: (newItem) => this.router.navigate(['/{lower_class_name}s', newItem.{primary_key}]),
        error: (err) => {{
          this.error = 'Error al crear';
          this.submitting = false;
          console.error(err);
        }}
      }});
    }}
  }}
}}"""



def generate_form_component_html(request: GenerateRequest) -> str:
    class_name = request.name
    lower_class_name = class_name.lower()
    primary_key = request.primary_key.name
    attributes = request.attributes
    auto_increment = request.auto_increment
    inputs = ""

    # Incluir el campo de la primary key solo si no es autoincrementable y no está ya en los atributos
    if not auto_increment and not any(attr.name == primary_key for attr in attributes):
        inputs += f"""<div class="col-md-6">
  <label class="form-label">{primary_key.capitalize()} *</label>
  <input type="number" formControlName="{primary_key}" class="form-control" required>
</div>
"""

    for attr in attributes:
        if auto_increment and attr.name == primary_key:
            continue  # saltar el id si es autoincremental y ya está en attributes

        label = attr.name.capitalize()
        name = attr.name
        required = " *" if attr.isRequired else ""
        input_type = "text"

        if attr.type.lower() in ["number", "int", "float", "double"]:
            input_type = "number"
        elif attr.type.lower() in ["date", "datetime"]:
            input_type = "datetime-local"
        elif attr.type.lower() == "boolean":
            input_type = "checkbox"

        if input_type == "checkbox":
            inputs += f"""<div class="col-md-12">
  <div class="form-check">
    <input type="checkbox" class="form-check-input" formControlName="{name}" id="{name}">
    <label for="{name}" class="form-check-label">{label}{required}</label>
  </div>
</div>
"""
        else:
            inputs += f"""<div class="col-md-6">
  <label class="form-label">{label}{required}</label>
  <input type="{input_type}" formControlName="{name}" class="form-control">
</div>
"""

    return f"""<div class="container mt-4">
  <div class="row mb-4">
    <div class="col-md-8">
      <h1>{{{{ isEditMode ? 'Editar' : 'Crear' }}}} {class_name}</h1>
    </div>
    <div class="col-md-4 text-end">
      <a [routerLink]="['/{lower_class_name}s']" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Volver
      </a>
    </div>
  </div>

  <div class="card shadow-sm">
    <div class="card-body">
      <div *ngIf="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2">Cargando...</p>
      </div>

      <div *ngIf="error" class="alert alert-danger">
        {{{{ error }}}}
      </div>

      <form *ngIf="!loading" [formGroup]="form" (ngSubmit)="onSubmit()" class="row g-3">
        {inputs.strip()}

        <div class="col-12 text-end">
          <button type="submit" class="btn btn-primary" [disabled]="submitting">
            <span *ngIf="submitting" class="spinner-border spinner-border-sm me-1"></span>
            {{{{ isEditMode ? 'Actualizar' : 'Crear' }}}}
          </button>
        </div>
      </form>
    </div>
  </div>
</div>"""


def generate_form_component_scss() -> str:
    return """.card {
  background-color: #1e293b;
  border: none;
  border-radius: 0.5rem;
}

.form-label {
  color: #f8fafc;
}

.form-control {
  background-color: #263548;
  border-color: #334155;
  color: #f8fafc;
}

.form-control:focus {
  background-color: #263548;
  border-color: #3f51b5;
  box-shadow: 0 0 0 0.25rem rgba(63, 81, 181, 0.25);
  color: #f8fafc;
}

.btn {
  min-width: 120px;
}
"""

