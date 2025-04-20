def generate_global_files(app_name: str):
    return {
        "angular.json": _angular_json(app_name),
        "package.json": _package_json(),
        "tsconfig.json": _tsconfig(),
        "tsconfig.app.json": _tsconfig_app(),
        "tsconfig.spec.json": _tsconfig_spec(),
        "src/index.html": _index_html(),
        "src/main.ts": _main_ts(),
        "src/styles.scss": _styles_scss(),
        "README.md": _readme()
    }

def _styles_scss():
    return """@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@300;400;500&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Oswald', sans-serif;
  background-color: #0f172a;
  color: white;
}
"""


def _angular_json(app_name: str):
    return f"""{{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {{
    "{app_name}": {{
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
            "outputPath": "dist/{app_name}",
            "index": "src/index.html",
            "main": "src/main.ts",
            "polyfills": [
              "zone.js"
            ],
            "tsConfig": "tsconfig.app.json",
            "inlineStyleLanguage": "scss",
            "assets": [
              "src/favicon.ico",
              "src/assets"
            ],
            "styles": [
              "src/styles.scss"
            ],
            "scripts": []
          }},
          "configurations": {{
            "production": {{
              "budgets": [
                {{
                  "type": "initial",
                  "maximumWarning": "500kb",
                  "maximumError": "1mb"
                }},
                {{
                  "type": "anyComponentStyle",
                  "maximumWarning": "2kb",
                  "maximumError": "4kb"
                }}
              ],
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
              "browserTarget": "{app_name}:build:production"
            }},
            "development": {{
              "browserTarget": "{app_name}:build:development"
            }}
          }},
          "defaultConfiguration": "development"
        }},
        "extract-i18n": {{
          "builder": "@angular-devkit/build-angular:extract-i18n",
          "options": {{
            "browserTarget": "{app_name}:build"
          }}
        }},
        "test": {{
          "builder": "@angular-devkit/build-angular:karma",
          "options": {{
            "polyfills": [
              "zone.js",
              "zone.js/testing"
            ],
            "tsConfig": "tsconfig.spec.json",
            "inlineStyleLanguage": "scss",
            "assets": [
              "src/favicon.ico",
              "src/assets"
            ],
            "styles": [
              "src/styles.scss"
            ],
            "scripts": []
          }}
        }}
      }}
    }}
  }}
}}"""

def _package_json():
    return """{
  "name": "angular-ui-app",
  "version": "0.1.0",
  "scripts": {
    "ng": "ng",
    "start": "ng serve",
    "build": "ng build",
    "test": "ng test"
  },
  "private": true,
  "dependencies": {
    "@angular/core": "^16.2.0",
    "@angular/common": "^16.2.0",
    "@angular/forms": "^16.2.0",
    "@angular/platform-browser": "^16.2.0",
    "@angular/platform-browser-dynamic": "^16.2.0",
    "@angular/router": "^16.2.0",
    "rxjs": "~7.8.0",
    "tslib": "^2.3.0",
    "zone.js": "~0.13.0"
  },
  "devDependencies": {
    "@angular-devkit/build-angular": "^16.2.0",
    "@angular/cli": "~16.2.0",
    "@angular/compiler-cli": "^16.2.0",
    "typescript": "~5.1.3"
  }
}"""

def _tsconfig():
    return """{
  "compileOnSave": false,
  "compilerOptions": {
    "baseUrl": "./",
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": false,
    "noImplicitReturns": true,
    "moduleResolution": "node",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "lib": ["ES2022", "dom"]
  }
}"""

def _tsconfig_app():
    return """{
  "extends": "./tsconfig.json",
  "files": ["src/main.ts"]
}"""

def _tsconfig_spec():
    return """{
  "extends": "./tsconfig.json",
  "include": ["src/**/*.spec.ts"]
}"""

def _index_html():
    return """<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <title>Angular UI</title>
    <base href="/">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet">
  </head>
  <body>
    <app-root></app-root>
  </body>
</html>"""

def _main_ts():
    return """import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));"""



def _readme():
    return """# Proyecto Angular Generado Automáticamente

Este proyecto fue creado por el backend con FastAPI para generar componentes UI en Angular de forma visual y modular.
"""
