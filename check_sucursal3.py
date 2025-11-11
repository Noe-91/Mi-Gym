import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migym_registro.settings.local')
django.setup()

from aplications.ocupacion.models import Acceso
from aplications.socios.models import Socio

# Ver todos los registros de la Sucursal 3 (Mi-Gym Norte)
print("\n" + "="*70)
print("REGISTROS DE ACCESO - SUCURSAL 3 (Mi-Gym Norte)")
print("="*70)

accesos = Acceso.objects.filter(sucursal_id=3).order_by('socio', '-fecha_hora')

socio_actual = None
for acc in accesos:
    if socio_actual != acc.socio_id:
        if socio_actual is not None:
            print("")  # Línea en blanco entre socios
        socio_actual = acc.socio_id
        socio = Socio.objects.get(id=acc.socio_id)
        print(f"\n👤 {socio.nombre} {socio.apellido}:")
    
    print(f"   {acc.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')} - {acc.tipo}")

# Ahora verificar quiénes aparecen como "dentro"
print("\n" + "="*70)
print("ANÁLISIS DE ÚLTIMA ACCIÓN POR SOCIO")
print("="*70)

socios_ids = Acceso.objects.filter(sucursal_id=3).values_list('socio_id', flat=True).distinct()

dentro_count = 0
for sid in socios_ids:
    ultimo = Acceso.objects.filter(socio_id=sid, sucursal_id=3).order_by('-fecha_hora').first()
    socio = Socio.objects.get(id=sid)
    
    estado = "🟢 DENTRO" if ultimo.tipo == "Ingreso" else "🔴 FUERA"
    print(f"{estado} - {socio.nombre} {socio.apellido} (último: {ultimo.tipo})")
    
    if ultimo.tipo == "Ingreso":
        dentro_count += 1

print(f"\n{'='*70}")
print(f"TOTAL PERSONAS DENTRO: {dentro_count}")
print(f"{'='*70}\n")
