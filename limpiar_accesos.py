import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migym_registro.settings.local')
django.setup()

from aplications.ocupacion.models import Acceso
from aplications.socios.models import Socio

# Buscar el socio
email = 'noeliasramoss17@gmail.com'
socio = Socio.objects.get(email=email)

# Eliminar TODOS los accesos de este socio para empezar limpio
count = Acceso.objects.filter(socio=socio).delete()[0]

print(f"\n{'='*60}")
print(f"✓ Eliminados {count} registros de acceso para {socio.nombre} {socio.apellido}")
print(f"{'='*60}\n")
