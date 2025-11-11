# MiGym - AI Coding Agent Instructions

## Project Overview
Django-based gym management system with dual-interface architecture: admin dashboard for staff and member portal for gym members ("socios"). Features real-time occupancy tracking, QR-based access control, subscription management, workout routines, and payments.

## Architecture

### Settings Structure
- **Split settings**: `migym_registro/settings/base.py` (shared) + `local.py` (dev)
- Always use: `DJANGO_SETTINGS_MODULE=migym_registro.settings.local`
- Secrets stored in root `secrets.json` (never commit)
- SQLite database: `db.sqlite3` (development)

### App Organization
```
aplications/
├── socios/        # Members: Socio, Suscripcion, Plan, Sucursal, Instructor
├── pagos/         # Payment processing and records
├── rutina/        # Workout routines (Ejercicio, Rutina, RutinaAsignacion)
├── ocupacion/     # Real-time occupancy tracking, access control API
├── configuracion/ # CRUD admin for Plans, Sucursales, Ejercicios, Rutinas
└── usuarios/      # User management (admin only)
core/              # Utilities (in_group helper, management commands)
```

### User Roles & Authentication
- **Staff/Admin**: Access admin dashboard via `@user_passes_test(lambda u: u.is_staff)`
- **Socio (Member)**: Check role with `in_group(user, "Socio")` from `core.utils`
- Login redirects: Staff → `/dash/admin/`, Socios → `/socios/panel/`
- Custom login: `core.views.CustomLoginView` checks `socio.activo` before allowing login

### Key Models & Relationships
- `Socio.user` → OneToOne with Django User (created automatically via signal)
- `Socio.email` is unique identifier (used for QR codes and API access)
- `Suscripcion.estado`: "Pendiente" (unpaid), "Vigente", "Vencida", "Pausada"
- `Acceso.tipo`: "Ingreso"/"Egreso" - tracks member check-ins/check-outs
- `ActiveSession`: Real-time occupancy (ACTIVE/CLOSED/AUTO_CLOSED)

## Critical Patterns

### Signal-Driven User Creation
When creating `Socio`, a post_save signal (`aplications/socios/signals.py`):
1. Creates Django User with `username=socio.email`
2. Adds user to "Socio" group
3. Sends password-reset email for first login
**Never manually create User objects for socios - let the signal handle it**

### Access Control Logic (QR & RFID)
API endpoint: `POST /aplicaciones/ocupacion/api/access/`
- Header: `X-Device-Token: secret-token-123`
- Request type ("IN"/"OUT") is **ignored** for QR scans
- Logic auto-detects from last `Acceso` record:
  - Last was "Ingreso" → Next is "Egreso"
  - Last was "Egreso" or no records → Next is "Ingreso"
- Creates both `AccessEvent` (audit) and `Acceso` (main record)
- Updates `ActiveSession` for real-time occupancy count

### Custom Confirmation Modal
Use `data-confirm` attributes on links/forms/buttons (not JavaScript `confirm()`):
```html
<a href="..." 
   data-confirm="¿Eliminar socio X?"
   data-confirm-ok="Eliminar"
   data-confirm-cancel="Cancelar">Delete</a>
```
Handled by `static/js/mg-confirm.js` - consistent UI across all CRUD operations

### Template Inheritance
- `base.html` → Foundation (includes mg-confirm modal)
- `base_dash.html` → Extends base, adds sidebar (admin or socio based on user role)
- All CRUD templates extend `base_dash.html`
- Sidebar selection: Check `{% if user.is_staff %}` → include `sidebar_admin.html`, else `sidebar_socio.html`

### URL Namespaces
All apps use namespaces - always reference with `app_name:view_name`:
```python
# In urls.py
app_name = "socios"  # Required

# In templates/views
reverse("socios:lista")  # ✓ Correct
reverse("lista")         # ✗ Wrong
```

## Development Workflows

### Running the Server
```powershell
cd Mi-Gym
python manage.py runserver
# Default: http://127.0.0.1:8000
```

### Database Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Testing Access Control API
Use `test_api.py` (sets up Django env, queries Socio/Acceso)
```powershell
python test_api.py
```

### Utility Scripts (All Set DJANGO_SETTINGS_MODULE)
- `check_accesos.py` - Verify access records
- `check_ocupacion.py` - Check occupancy state
- `limpiar_sesiones.py` - Clean up sessions
- `limpiar_accesos.py` - Clean access logs

### Loading Demo Data
```powershell
python manage.py cargar_datos_demo
```

## QR Code System

### Member QR Generation
Each socio gets unique QR containing their email:
```python
# View: socios.views.mi_qr
import qrcode
qr = qrcode.make(socio.email)
# Rendered as base64 in template
```

### QR Scanner
Use `tools/simulador_qr.html` (opens in browser):
- Requires server running on localhost:8000
- Uses html5-qrcode library
- Scans QR → Extracts email → POSTs to API with `member_code=email`

## Project-Specific Conventions

### Form Validation
Forms in `aplications/*/forms.py` use Django's ModelForm:
- Add `help_text` and custom `clean_*` methods for business logic
- Example: `Socio.dni` uses RegexValidator in model (7-10 digits)

### Bootstrap 5.3.3
All templates use Bootstrap classes:
- Cards: `.card`, `.card-body`, `.card-header`
- Buttons: `.btn-primary`, `.btn-danger`, `.btn-outline-secondary`
- Forms: `.form-label`, `.form-control`, `.form-select`

### Spanish Language
- Model verbose names in Spanish
- Template text in Spanish
- Choice fields use Spanish labels: `("Vigente", "Vigente")`

### Static Files Organization
```
static/
├── css/
│   ├── mg-confirm.css       # Custom modal styles
│   ├── sidebar_admin.css    # Admin sidebar
│   └── nav_home.css         # Top navbar
└── js/
    └── mg-confirm.js        # Confirmation modal logic
```

### Date/Time Handling
- Use `django.utils.timezone.now()` (not datetime.now())
- Date comparisons: `timezone.localdate()` for dates
- `Suscripcion` date validation: `fecha_inicio <= fecha_fin`

## Common Pitfalls

1. **Don't create User objects directly** - Socio signal handles it
2. **Never hardcode URLs** - Use `{% url 'namespace:name' %}` with namespaces
3. **Access control API**: Don't trust client's "IN"/"OUT" - server decides from DB
4. **Occupancy count**: Use `ActiveSession.objects.filter(status="ACTIVE").count()`
5. **Login redirects**: Use `LOGIN_REDIRECT_URL = "role_redirect"` (not hardcoded paths)
6. **Email as identifier**: `Socio.email` is unique and used for QR - never DNI
7. **Settings module**: All standalone scripts must set `DJANGO_SETTINGS_MODULE=migym_registro.settings.local`

## Documentation References
- `CONFIGURACION_README.md` - CRUD configuration module details
- `PANEL_SOCIO_README.md` - Member portal features and URLs
- `QR_SYSTEM_README.md` - QR generation and access control flow
- `docs/suscripciones.md` - Subscription business rules
