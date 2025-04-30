import os
import zipfile
import re

def generar_angular(texto_gemini: str, carpeta_destino: str):
    os.makedirs(carpeta_destino, exist_ok=True)
    crear_estructura_angular(carpeta_destino)

    app_dir = os.path.join(carpeta_destino, "src", "app")

    # Insertar Bootstrap en index.html
    index_path = os.path.join(carpeta_destino, "src", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    bootstrap_tag = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">\n'
    contenido = contenido.replace("</head>", f"{bootstrap_tag}</head>")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(contenido)

    # Extraer y guardar HTML desde Gemini
    html_code = extraer_html_desde_gemini(texto_gemini)
    with open(os.path.join(app_dir, "app.component.html"), "w", encoding="utf-8") as f:
        f.write(html_code)

    # Guardar app.component.ts
    with open(os.path.join(app_dir, "app.component.ts"), "w", encoding="utf-8") as f:
        f.write(generar_app_component_ts())

    # Guardar app.component.css vacío
    with open(os.path.join(app_dir, "app.component.css"), "w", encoding="utf-8") as f:
        f.write("")

    # Guardar main.ts
    main_ts_path = os.path.join(carpeta_destino, "src", "main.ts")
    with open(main_ts_path, "w", encoding="utf-8") as f:
        f.write(generar_main_ts())

    # styles.css (opcional pero común)
    with open(os.path.join(carpeta_destino, "src", "styles.css"), "w", encoding="utf-8") as f:
        f.write("/* Estilos globales */")

def crear_estructura_angular(carpeta_destino: str):
    os.makedirs(os.path.join(carpeta_destino, "src", "app"), exist_ok=True)

    with open(os.path.join(carpeta_destino, "angular.json"), "w", encoding="utf-8") as f:
        f.write("""{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "defaultProject": "app",
  "projects": {
    "app": {
      "root": "",
      "projectType": "application",
      "sourceRoot": "src",
      "prefix": "app",
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:browser",
          "options": {
            "outputPath": "dist/app",
            "index": "src/index.html",
            "main": "src/main.ts",
            "tsConfig": "tsconfig.app.json",
            "assets": ["src/favicon.ico", "src/assets"],
            "styles": ["src/styles.css"],
            "scripts": []
          }
        },
        "serve": {
          "builder": "@angular-devkit/build-angular:dev-server",
          "options": {
            "buildTarget": "app:build"
          }
        }
      }
    }
  }
}
""")

    with open(os.path.join(carpeta_destino, "package.json"), "w", encoding="utf-8") as f:
        f.write("""{
  "name": "angular_proyecto",
  "version": "0.0.0",
  "scripts": {
    "ng": "ng",
    "start": "ng serve",
    "build": "ng build"
  },
  "dependencies": {
    "@angular/animations": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/compiler": "^17.0.0",
    "@angular/core": "^17.0.0",
    "@angular/forms": "^17.0.0",
    "@angular/platform-browser": "^17.0.0",
    "@angular/platform-browser-dynamic": "^17.0.0",
    "@angular/router": "^17.0.0",
    "rxjs": "^7.8.1",
    "tslib": "^2.6.2",
    "zone.js": "^0.14.0"
  },
  "devDependencies": {
    "@angular/cli": "^17.0.0",
    "@angular/compiler-cli": "^17.0.0",
    "@angular-devkit/build-angular": "^17.0.0",
    "typescript": "^5.2.0"
  }
}""")

    with open(os.path.join(carpeta_destino, "tsconfig.json"), "w", encoding="utf-8") as f:
        f.write("""{
  "compileOnSave": false,
  "compilerOptions": {
    "baseUrl": "./",
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "sourceMap": true,
    "declaration": false,
    "moduleResolution": "node",
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "target": "es2022",
    "module": "es2022",
    "useDefineForClassFields": false,
    "lib": ["es2022", "dom"]
  }
}""")

    with open(os.path.join(carpeta_destino, "tsconfig.app.json"), "w", encoding="utf-8") as f:
        f.write("""{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/app",
    "types": []
  },
  "files": ["src/main.ts"],
  "include": ["src/**/*.d.ts"]
}""")

    index_html_path = os.path.join(carpeta_destino, "src", "index.html")
    os.makedirs(os.path.dirname(index_html_path), exist_ok=True)
    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>AngularProyecto</title>
    <base href="/" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  </head>
  <body>
    <app-root></app-root>
  </body>
</html>
""")

def extraer_html_desde_gemini(texto: str) -> str:
    match = re.search(r'```html(.*?)```', texto, re.DOTALL)
    if match:
        html = match.group(1).strip()
        return html
    else:
        return "<div class='container'><h3>No se encontró HTML en la respuesta de Gemini.</h3></div>"

def generar_app_component_ts() -> str:
    return """import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'angular_proyecto';
}
"""

def generar_main_ts() -> str:
    return """import "zone.js"
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { importProvidersFrom } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { FormsModule } from '@angular/forms';

bootstrapApplication(AppComponent, {
  providers: [
    provideHttpClient(),
    provideRouter([]),
    importProvidersFrom(FormsModule)
  ]
}).catch(err => console.error(err));
"""

def comprimir_proyecto(carpeta: str, zip_path: str):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(carpeta):
            for file in files:
                ruta_completa = os.path.join(root, file)
                ruta_zip = os.path.relpath(ruta_completa, carpeta)
                zipf.write(ruta_completa, ruta_zip)
