def generate_component_files(components, background_color):
    files = {}
    unique_types = set()

    def collect(component):
        unique_types.add(component.type)
        for child in getattr(component, "children", []):
            collect(child)

    for component in components:
        collect(component)

    for comp_type in unique_types:
        component_name = comp_type
        class_name = to_pascal_case(component_name) + "Component"

        files[f"src/app/components/{component_name}/{component_name}.component.ts"] = generate_component_ts(component_name, class_name)
        files[f"src/app/components/{component_name}/{component_name}.component.html"] = generate_component_html(component_name)
        files[f"src/app/components/{component_name}/{component_name}.component.scss"] = generate_component_scss(component_name)

    return files


def generate_component_ts(component_name, class_name):
    if component_name == "button":
        return f"""import {{ Component, Input, OnInit }} from '@angular/core';

@Component({{
  selector: 'app-{component_name}',
  templateUrl: './{component_name}.component.html',
  styleUrls: ['./{component_name}.component.scss']
}})
export class {class_name} implements OnInit {{
  @Input() props: any = {{}};

  constructor() {{ }}

  ngOnInit(): void {{ }}

  handleClick(event: Event): void {{
    event.stopPropagation();
    console.log('Botón clickeado:', this.props.text || 'Botón');
  }}
}}"""
    else:
        return f"""import {{ Component, Input }} from '@angular/core';

@Component({{
  selector: 'app-{component_name}',
  templateUrl: './{component_name}.component.html',
  styleUrls: ['./{component_name}.component.scss']
}})
export class {class_name} {{
  @Input() props: any = {{}};
}}"""


def generate_component_html(component_name):
    if component_name == "button":
        return """<button 
  class="component-button" 
  (click)="handleClick($event)"
  [ngStyle]="{
    'background-color': props.backgroundColor || '#3f51b5',
    'color': props.color || '#ffffff',
    'border-radius': props.borderRadius || '4px',
    'padding': props.padding || '8px 16px',
    'font-size': props.fontSize || '16px',
    'font-weight': props.fontWeight || 'normal'
  }"
>
  {{ props.text || 'Botón' }}
</button>"""

    elif component_name == "input":
        return """<input 
  class="component-input" 
  [(ngModel)]="props.value"
  [placeholder]="props.placeholder || 'Texto...'"
  [ngStyle]="{
    'padding': props.padding || '8px',
    'font-size': props.fontSize || '16px',
    'border-radius': props.borderRadius || '4px',
    'border': props.border || '1px solid #ccc'
  }"
/>"""

    elif component_name == "textarea":
        return """<textarea 
  class="component-textarea"
  [(ngModel)]="props.value"
  [placeholder]="props.placeholder || 'Texto largo...'"
  [ngStyle]="{
    'padding': props.padding || '8px',
    'font-size': props.fontSize || '16px',
    'border-radius': props.borderRadius || '4px',
    'border': props.border || '1px solid #ccc'
  }"
></textarea>"""

    elif component_name == "select":
        return """<select 
  class="component-select"
  [(ngModel)]="props.value"
  [ngStyle]="{
    'padding': props.padding || '8px',
    'border-radius': props.borderRadius || '4px',
    'font-size': props.fontSize || '16px'
  }"
>
  <option *ngFor="let opt of props.options || []" [value]="opt">{{ opt }}</option>
</select>"""

    elif component_name == "checkbox":
        return """<label class="component-checkbox">
  <input type="checkbox" [(ngModel)]="props.checked" />
  {{ props.label || 'Casilla' }}
</label>"""

    elif component_name == "navbar":
        return """<nav class="component-navbar" [ngStyle]="props">
  <span>{{ props.title || 'Navbar' }}</span>
  <div *ngIf="props.links">
    <a *ngFor="let link of props.links"
       [routerLink]="['/', link]"
       routerLinkActive="active"
       style="margin-left: 12px; text-decoration: none; color: inherit;">
      {{ link | titlecase }}
    </a>
  </div>
</nav>"""


    elif component_name == "image":
        return """<img 
  class="component-image" 
  [src]="props.src || 'assets/placeholder.png'"
  [alt]="props.alt || 'Imagen'"
  [ngStyle]="{
    'object-fit': props.objectFit || 'cover',
    'border-radius': props.borderRadius || '4px'
  }"
/>"""

    elif component_name == "table":
        return """<table class="component-table">
  <thead>
    <tr>
      <th *ngFor="let header of props.headers">{{ header }}</th>
    </tr>
  </thead>
  <tbody>
    <tr *ngFor="let row of props.rows">
      <td *ngFor="let cell of row">{{ cell }}</td>
    </tr>
  </tbody>
</table>"""


    elif component_name == "text":
        return """<p 
  class="component-text"
  [ngStyle]="{
    'color': props.color || '#ffffff',
    'font-size': props.fontSize || '16px',
    'font-weight': props.fontWeight || 'normal',
    'text-align': props.textAlign || 'left'
  }"
>
  {{ props.text || 'Texto de ejemplo' }}
</p>"""

    elif component_name == "list":
        return """<ul class="component-list" [ngStyle]="props">
  <li *ngFor="let item of props.items || ['Elemento 1', 'Elemento 2']">{{ item }}</li>
</ul>"""

    elif component_name == "card":
        return """<div class="component-card" [ngStyle]="props">
  <h3>{{ props.title || 'Título de tarjeta' }}</h3>
  <p>{{ props.content || 'Contenido de la tarjeta' }}</p>
</div>"""

    elif component_name == "container":
        return """<div class="component-container" [ngStyle]="{
  'background-color': props.backgroundColor || '#1e293b',
  'border-radius': props.borderRadius || '4px',
  'padding': props.padding || '16px'
}">
  <ng-content></ng-content>
</div>"""

    else:
        return f"""<div class="component-{component_name}" [ngStyle]="props">
  {{ props.text || '{component_name}' }}
</div>"""


def generate_component_scss(component_name):
    if component_name == "button":
        return """.component-button {
  cursor: pointer;
  border: none;
  font-family: 'Oswald', sans-serif;
  transition: background-color 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  width: 100%;
  height: 100%;
  margin: 0;
  box-sizing: border-box;

  &:hover {
    filter: brightness(1.1);
  }

  &:active {
    transform: translateY(1px);
  }
}"""

    elif component_name == "input":
        return """.component-input {
  width: 100%;
  height: 100%;
  font-family: 'Oswald', sans-serif;
  padding: 8px;
  box-sizing: border-box;
  background-color: white;
  border: 1px solid #ccc;
}"""

    elif component_name == "table":
        return """.component-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Oswald', sans-serif;
  background-color: #ffffff;
  color: #0f172a;

  th, td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
  }

  thead {
    background-color: #e2e8f0;
  }

  tbody tr:nth-child(even) {
    background-color: #f8fafc;
  }
}"""



    elif component_name == "textarea":
        return """.component-textarea {
  width: 100%;
  height: 100%;
  resize: none;
  font-family: 'Oswald', sans-serif;
  padding: 8px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}"""

    elif component_name == "select":
        return """.component-select {
  width: 100%;
  height: 100%;
  font-family: 'Oswald', sans-serif;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}"""

    elif component_name == "checkbox":
        return """.component-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Oswald', sans-serif;
}"""

    elif component_name == "navbar":
        return """.component-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  font-family: 'Oswald', sans-serif;
  height: 100%;

  a {
    color: inherit;
    text-decoration: none;
    margin-left: 12px;

    &:hover {
      text-decoration: underline;
    }
  }
}"""

    elif component_name == "text":
        return """.component-text {
  font-family: 'Oswald', sans-serif;
  margin: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}"""

    elif component_name == "image":
        return """.component-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
  display: block;
}"""

    elif component_name == "list":
        return """.component-list {
  list-style: disc;
  font-family: 'Oswald', sans-serif;
  padding-left: 20px;
  margin: 0;

  li {
    margin-bottom: 4px;
  }
}"""

    elif component_name == "card":
        return """.component-card {
  background-color: #1e293b;
  color: #ffffff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  font-family: 'Oswald', sans-serif;

  h3 {
    margin: 0 0 8px 0;
  }

  p {
    margin: 0;
  }
}"""

    elif component_name == "container":
        return """.component-container {
  width: 100%;
  height: 100%;
  background-color: #1e293b;
  padding: 16px;
  border-radius: 8px;
  box-sizing: border-box;
}"""

    else:
        return f""".component-{component_name} {{
  width: 100%;
  height: 100%;
  font-family: 'Oswald', sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
}}"""


def to_pascal_case(s: str):
    return ''.join(word.capitalize() for word in s.split('-'))
