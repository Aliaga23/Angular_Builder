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
  [disabled]="props.disabled"
  [attr.type]="props.type || 'button'"
  [ngStyle]="{
    'background-color': props.backgroundColor || '#3f51b5',
    'color': props.color || '#ffffff',
    'border-radius': props.borderRadius || '4px',
    'padding': props.padding || '8px 16px',
    'font-size': props.fontSize || '16px',
    'font-weight': props.fontWeight || 'normal',
    'width': props.width,
    'height': props.height
  }"
>
  {{ props.text || 'Botón' }}
</button>"""

    elif component_name == "text":
        return """<p class="component-text" [ngStyle]="{
  'color': props.color || '#ffffff',
  'font-size': props.fontSize || '16px',
  'font-weight': props.fontWeight || 'normal',
  'text-align': props.textAlign || 'left',
  'width': props.width,
  'height': props.height
}">
  {{ props.text || 'Texto de ejemplo' }}
</p>"""

    elif component_name == "datepicker":
        return """<label *ngIf="props.label">{{ props.label }}</label>
<input type="date"
  class="component-datepicker"
  [(ngModel)]="props.value"
  [placeholder]="props.placeholder"
  [min]="props.min"
  [max]="props.max"
  [required]="props.required || null"
  [disabled]="props.disabled || null"
  [ngStyle]="{
    'padding': props.padding || '8px',
    'font-size': props.fontSize || '16px',
    'border-radius': props.borderRadius || '4px',
    'border': props.border || '1px solid #ccc',
    'width': props.width,
    'height': props.height
  }"
/>"""

    elif component_name == "grid":
        return """<div class="component-grid"
  [ngStyle]="{
    'display': 'grid',
    'grid-template-columns': 'repeat(' + (props.columns || 3) + ', 1fr)',
    'gap': (props.gap || 16) + 'px',
    'width': props.width + 'px',
    'min-height': props.minHeight + 'px',
    'background-color': props.backgroundColor,
    'color': props.color
  }">
  <ng-content></ng-content>
</div>"""

    elif component_name == "list":
        return """<ul class="component-list" [ngStyle]="{
  'width': props.width,
  'height': props.height
}">
  <li *ngFor="let item of props.items">
    {{ item }}
  </li>
</ul>"""

    elif component_name == "heading":
        return """<ng-container [ngSwitch]="props.level || 'h1'">
  <h1 *ngSwitchCase="'h1'" class="component-heading">{{ props.text }}</h1>
  <h2 *ngSwitchCase="'h2'" class="component-heading">{{ props.text }}</h2>
  <h3 *ngSwitchCase="'h3'" class="component-heading">{{ props.text }}</h3>
  <h4 *ngSwitchCase="'h4'" class="component-heading">{{ props.text }}</h4>
  <h5 *ngSwitchCase="'h5'" class="component-heading">{{ props.text }}</h5>
  <h6 *ngSwitchCase="'h6'" class="component-heading">{{ props.text }}</h6>
</ng-container>"""

    elif component_name == "image":
        return """<img 
  class="component-image" 
  [src]="props.src || 'assets/placeholder.png'"
  [alt]="props.alt || 'Imagen'"
  [ngStyle]="{
    'width': props.width + 'px',
    'height': props.height + 'px',
    'object-fit': props.objectFit || 'cover',
    'border-radius': props.borderRadius || '4px'
  }"
  [attr.loading]="props.lazy ? 'lazy' : 'eager'"
  (error)="props.src = props.fallback || 'assets/placeholder.png'"
/>"""

    elif component_name == "select":
        return """<label *ngIf="props.label">{{ props.label }}</label>
<select 
  class="component-select"
  [(ngModel)]="props.value"
  [disabled]="props.disabled"
  [attr.required]="props.required || null"
  [multiple]="props.multiple || null"
  [ngStyle]="{
    'padding': props.padding || '8px',
    'border-radius': props.borderRadius || '4px',
    'font-size': props.fontSize || '16px',
    'width': props.width,
    'height': props.height
  }"
>
  <option *ngIf="props.placeholder" disabled selected>{{ props.placeholder }}</option>
  <option *ngFor="let opt of props.options" [value]="opt.value">{{ opt.label }}</option>
</select>"""

    elif component_name == "table":
        return """<table class="component-table" [ngStyle]="{ 'font-size': props.fontSize || '14px' }">
  <caption *ngIf="props.caption">{{ props.caption }}</caption>
  <thead *ngIf="props.showHeader">
    <tr>
      <th *ngFor="let col of props.columns">{{ col.header }}</th>
    </tr>
  </thead>
  <tbody>
    <tr *ngFor="let row of props.data">
      <td *ngFor="let col of props.columns">{{ row[col.accessor] }}</td>
    </tr>
  </tbody>
</table>"""

    elif component_name == "sidebar":
        return """<aside class="component-sidebar" [ngStyle]="{
  'width': props.width + 'px',
  'background-color': props.backgroundColor || '#1e293b',
  'color': props.color || '#000000',
  'padding': props.padding || '16px'
}">
  <div class="sidebar-header" *ngIf="props.title">
    <h2>{{ props.title }}</h2>
  </div>
  <nav class="sidebar-links" *ngIf="props.items">
    <a *ngFor="let item of props.items"
       href="#"
       [ngStyle]="{ 'margin-bottom': '12px', 'display': 'flex', 'align-items': 'center', 'gap': '8px', 'text-decoration': 'none', 'color': 'inherit' }">
      <i *ngIf="item.icon" [class]="'icon-' + item.icon"></i>
      {{ item.label }}
    </a>
  </nav>
</aside>"""

    elif component_name == "checkbox":
        return """<label class="component-checkbox">
  <input type="checkbox" [(ngModel)]="props.checked" 
    [disabled]="props.disabled"
    [attr.required]="props.required || null"
    [indeterminate]="props.indeterminate || null" />
  {{ props.label || 'Casilla' }}
</label>"""
    elif  component_name == "input":
        return """<label *ngIf="props.label">{{ props.label }}</label>
<input 
  class="component-input" 
  [(ngModel)]="props.value"
  [type]="props.type || 'text'"
  [placeholder]="props.placeholder || 'Texto...'"
  [disabled]="props.disabled"
  [attr.required]="props.required || null"
  [attr.maxLength]="props.maxLength || null"
  [attr.minLength]="props.minLength || null"
  [ngStyle]="{
    'padding': props.padding || '8px',
    'font-size': props.fontSize || '16px',
    'border-radius': props.borderRadius || '4px',
    'border': props.border || '1px solid #ccc',
    'width': props.width,
    'height': props.height
  }"
/>
<div *ngIf="props.error" class="error-message">{{ props.error }}</div>"""

    elif component_name == "textarea":
        return """<label *ngIf="props.label">{{ props.label }}</label>
<textarea 
  class="component-textarea"
  [(ngModel)]="props.value"
  [placeholder]="props.placeholder || 'Texto largo...'"
  [rows]="props.rows || 3"
  [disabled]="props.disabled"
  [attr.required]="props.required || null"
  [attr.maxLength]="props.maxLength || null"
  [ngStyle]="{
    'padding': props.padding || '8px',
    'font-size': props.fontSize || '16px',
    'border-radius': props.borderRadius || '4px',
    'border': props.border || '1px solid #ccc',
    'width': props.width,
    'height': props.height
  }"
></textarea>
<div *ngIf="props.error" class="error-message">{{ props.error }}</div>"""

    elif component_name == "card":
        return """<div class="component-card" [ngClass]="{ 'clickable': props.clickable }" [ngStyle]="{
  'background-color': props.backgroundColor || '#1e293b',
  'color': props.color || '#ffffff',
  'padding': props.padding || '16px',
  'border-radius': props.borderRadius || '8px',
  'box-shadow': props.elevation ? '0 ' + props.elevation + 'px ' + (props.elevation * 2) + 'px rgba(0,0,0,0.15)' : 'none',
  'width': props.width,
  'height': props.height
}">
  <img *ngIf="props.image" [src]="props.image" alt="Imagen" class="card-image" />
  <h3>{{ props.title || 'Título de tarjeta' }}</h3>
  <p>{{ props.content || 'Contenido de la tarjeta' }}</p>
  <div class="card-actions" *ngIf="props.actions?.length">
    <button *ngFor="let action of props.actions">{{ action }}</button>
  </div>
</div>"""

    elif component_name == "container":
        return """<div class="component-container" [ngStyle]="{
  'background-color': props.backgroundColor || '#1e293b',
  'border-radius': props.borderRadius || '4px',
  'padding': props.padding || '16px',
  'max-width': props.maxWidth || '1200px',
  'margin': props.centered ? '0 auto' : '0',
  'display': 'flex',
  'flex-direction': props.direction || 'column',
  'gap': props.spacing || '16px',
  'width': props.width,
  'height': props.height
}">
  <ng-content></ng-content>
</div>"""

    elif component_name == "slider":
        return """<div class="component-slider">
  <input type="range"
    [(ngModel)]="props.value"
    [min]="props.min || 0"
    [max]="props.max || 100"
    [step]="props.step || 1"
    [disabled]="props.disabled"
    [ngStyle]="{
      'width': props.width || '100%'
    }"
  />
  <span *ngIf="props.marks">{{ props.value }}</span>
</div>"""

    elif component_name == "link":
        return """<a class="component-link"
  [href]="props.href || '#'"
  [target]="props.target || '_self'"
  [rel]="props.rel"
  [ngStyle]="{
    'text-decoration': props.underline === false ? 'none' : 'underline',
    'color': props.color || '#3b82f6'
  }"
  [class.disabled]="props.disabled">
  {{ props.text || 'Enlace' }}
</a>"""
    elif component_name == "navbar":
        return """<nav class="component-navbar" [ngClass]="{ 'navbar-fixed': props.fixed, 'navbar-transparent': props.transparent }" [ngStyle]="props">
  <img *ngIf="props.logo" [src]="props.logo" alt="Logo" class="navbar-logo">
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
    elif component_name == "checklist":
        return """<div class="component-checklist">
  <label *ngIf="props.label" [ngStyle]="{ 'color': props.color || '#000000' }">{{ props.label }}</label>
  <div [ngStyle]="{
    'display': props.orientation === 'horizontal' ? 'flex' : 'block',
    'gap': '8px',
    'color': props.color || '#000000'
  }">
    <label *ngFor="let item of props.items" [ngStyle]="{ 'display': 'flex', 'align-items': 'center', 'gap': '4px' }">
      <input type="checkbox" [(ngModel)]="item.checked" />
      <span>{{ item.label }}</span>
    </label>
  </div>
</div>"""


    else:
        return f"""<div class="component-{component_name}" [ngStyle]="props">
  {{ props.text || '{component_name}' }}
</div>"""



def generate_component_scss(component_name):
    common_font = "font-family: 'Oswald', sans-serif;"

    if component_name == "button":
        return f""".component-button {{
  cursor: pointer;
  border: none;
  {common_font}
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;

  &:hover:not([disabled]) {{
    filter: brightness(1.1);
  }}

  &:active:not([disabled]) {{
    transform: translateY(1px);
  }}

  &:disabled {{
    opacity: 0.6;
    cursor: not-allowed;
  }}
}}"""

    elif component_name == "text":
        return f""".component-text {{
  {common_font}
  margin: 0;
  display: flex;
  align-items: center;
}}"""

    elif component_name == "datepicker":
        return f""".component-datepicker {{
  width: 100%;
  {common_font}
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
  background-color: white;
  color: #0f172a;
}}"""
    elif component_name == "navbar":
        return """.component-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  font-family: 'Oswald', sans-serif;
  height: 60px;
  background-color: #1e293b;
  color: white;
}

.navbar-fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
}

.navbar-transparent {
  background-color: transparent;
}

.navbar-logo {
  height: 40px;
  margin-right: 12px;
}"""
    elif component_name == "grid":
        return f""".component-grid {{
  {common_font}
  width: 100%;
  display: grid;
  gap: 16px;
  box-sizing: border-box;
}}"""

    elif component_name == "list":
        return f""".component-list {{
  list-style: disc;
  {common_font}
  padding-left: 20px;
  margin: 0;

  li {{
    margin-bottom: 4px;
  }}
}}"""

    elif component_name == "heading":
        return f""".component-heading {{
  {common_font}
  margin: 0;
  padding: 0;
  color: #0f172a;
}}"""

    elif component_name == "image":
        return f""".component-image {{
  display: block;
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  object-fit: cover;
}}"""

    elif component_name == "select":
        return f""".component-select {{
  width: 100%;
  {common_font}
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}}"""

    elif component_name == "table":
        return f""".component-table {{
  width: 100%;
  border-collapse: collapse;
  {common_font}
  background-color: #ffffff;
  color: #0f172a;

  th, td {{
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
  }}

  thead {{
    background-color: #e2e8f0;
  }}

  tbody tr:nth-child(even) {{
    background-color: #f8fafc;
  }}
}}"""

    elif component_name == "sidebar":
        return f""".component-sidebar {{
  height: 100vh;
  {common_font}
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow-y: auto;

  .sidebar-header {{
    margin-bottom: 16px;

    h2 {{
      margin: 0;
      font-size: 20px;
      font-weight: bold;
    }}
  }}

  .sidebar-links {{
    display: flex;
    flex-direction: column;

    a {{
      color: inherit;
      text-decoration: none;
      padding: 8px 12px;
      border-radius: 4px;
      transition: background-color 0.2s;

      &:hover {{
        background-color: rgba(0, 0, 0, 0.05);
      }}

      &.active {{
        background-color: rgba(0, 0, 0, 0.1);
        font-weight: bold;
      }}
    }}
  }}
}}"""

    elif component_name == "checkbox":
        return f""".component-checkbox {{
  display: flex;
  align-items: center;
  gap: 8px;
  {common_font}
}}"""

    elif component_name == "input":
        return f""".component-input {{
  width: 100%;
  {common_font}
  padding: 8px;
  box-sizing: border-box;
  background-color: white;
  border: 1px solid #ccc;
}}

.error-message {{
  color: red;
  font-size: 12px;
  margin-top: 4px;
}}"""

    elif component_name == "textarea":
        return f""".component-textarea {{
  width: 100%;
  resize: vertical;
  {common_font}
  padding: 8px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}}

.error-message {{
  color: red;
  font-size: 12px;
  margin-top: 4px;
}}"""

    elif component_name == "card":
        return f""".component-card {{
  background-color: #1e293b;
  color: #ffffff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  {common_font}

  h3 {{
    margin: 0 0 8px 0;
  }}

  p {{
    margin: 0;
  }}

  &.clickable {{
    cursor: pointer;
    transition: transform 0.1s;

    &:hover {{
      transform: scale(1.01);
    }}
  }}

  .card-image {{
    width: 100%;
    height: auto;
    border-radius: 4px;
    margin-bottom: 12px;
  }}

  .card-actions {{
    margin-top: 12px;

    button {{
      margin-right: 8px;
    }}
  }}
}}"""

    elif component_name == "container":
        return f""".component-container {{
  width: 100%;
  background-color: #1e293b;
  padding: 16px;
  border-radius: 8px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 16px;
  {common_font}
}}"""

    elif component_name == "slider":
        return f""".component-slider {{
  width: 100%;
  {common_font}

  input[type="range"] {{
    width: 100%;
    cursor: pointer;
    accent-color: #3b82f6;
  }}

  span {{
    display: block;
    margin-top: 4px;
    font-size: 14px;
    text-align: right;
    color: #0f172a;
  }}
}}"""

    elif component_name == "link":
        return f""".component-link {{
  {common_font}
  color: #3b82f6;
  text-decoration: underline;
  cursor: pointer;
  transition: opacity 0.2s;

  &:hover {{
    opacity: 0.8;
  }}

  &.disabled {{
    pointer-events: none;
    opacity: 0.6;
    cursor: not-allowed;
  }}
}}"""
    
    elif component_name == "checklist":
        return """.component-checklist {
  font-family: 'Oswald', sans-serif;
  display: flex;
  flex-direction: column;
  gap: 8px;

  label {
    font-weight: 500;
  }

  input[type="checkbox"] {
    margin-right: 6px;
  }
}"""

    else:
        return f""".component-{component_name} {{
  {common_font}
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}}"""


def to_pascal_case(s: str):
    return ''.join(word.capitalize() for word in s.split('-'))
