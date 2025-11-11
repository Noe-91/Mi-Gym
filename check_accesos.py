import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migym_registro.settings.local')
django.setup()

from aplications.ocupacion.models import Acceso
from aplications.socios.models import Socio

print("\n=== SOCIOS REGISTRADOS ===")
socios = Socio.objects.all()[:10]
for s in socios:
    print(f"Email: {s.email} - Nombre: {s.nombre} {s.apellido}")

print("\n=== TODOS LOS ACCESOS ===")
accesos = Acceso.objects.all().order_by('-fecha_hora')[:10]
for a in accesos:
    print(f"{a.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')} - {a.socio.email} - {a.tipo}")
