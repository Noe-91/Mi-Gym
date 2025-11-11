import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migym_registro.settings.local')
django.setup()

from aplications.ocupacion.models import Acceso
from django.db.models import OuterRef, Subquery

# Subconsulta: último tipo por socio
ultimo_tipo_subq = (
    Acceso.objects
    .filter(socio_id=OuterRef("socio_id"), sucursal_id=OuterRef("sucursal_id"))
    .order_by("-fecha_hora")
    .values("tipo")[:1]
)

# Obtener registros únicos con su último tipo
base = (
    Acceso.objects
    .values("socio_id", "sucursal_id")
    .distinct()
    .annotate(ultimo_tipo=Subquery(ultimo_tipo_subq))
)

print("\n" + "="*70)
print("ESTADO ACTUAL DE OCUPACIÓN")
print("="*70)

for item in base:
    socio_id = item['socio_id']
    tipo = item['ultimo_tipo']
    
    # Obtener nombre del socio
    from aplications.socios.models import Socio
    socio = Socio.objects.get(id=socio_id)
    
    print(f"Socio: {socio.nombre} {socio.apellido} - Último: {tipo}")

# Contar solo los que están "Ingreso"
dentro = base.filter(ultimo_tipo="Ingreso")
print(f"\n{'='*70}")
print(f"TOTAL PERSONAS DENTRO: {dentro.count()}")
print(f"{'='*70}\n")
