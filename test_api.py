import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migym_registro.settings.local')
django.setup()

from aplications.socios.models import Socio
from aplications.ocupacion.models import Acceso

# Buscar el socio
email = 'noeliasramoss17@gmail.com'
print(f"\n{'='*60}")
print(f"Buscando socio con email: {email}")

try:
    socio = Socio.objects.get(email=email)
    print(f"✓ Socio encontrado: {socio.nombre} {socio.apellido}")
    
    # Ver último acceso
    ultimo_acceso = Acceso.objects.filter(socio=socio).order_by('-fecha_hora').first()
    
    if ultimo_acceso:
        print(f"\nÚltimo acceso registrado:")
        print(f"  - Fecha: {ultimo_acceso.fecha_hora}")
        print(f"  - Tipo: {ultimo_acceso.tipo}")
        
        if ultimo_acceso.tipo == "Ingreso":
            print(f"\n✓ SIGUIENTE DEBE SER: EGRESO")
        else:
            print(f"\n✓ SIGUIENTE DEBE SER: INGRESO")
    else:
        print(f"\nNo hay accesos registrados")
        print(f"✓ SIGUIENTE DEBE SER: INGRESO")
        
except Socio.DoesNotExist:
    print(f"✗ Socio NO encontrado con ese email")

print(f"{'='*60}\n")
