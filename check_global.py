import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migym_registro.settings.local')
django.setup()

from aplications.ocupacion.models import Acceso
from aplications.socios.models import Socio, Sucursal

print("\n" + "="*80)
print("OCUPACIÓN GLOBAL - TODAS LAS SUCURSALES")
print("="*80)

# Por cada sucursal
sucursales = Sucursal.objects.all()

total_dentro = 0

for suc in sucursales:
    print(f"\n📍 {suc.nombre} (ID: {suc.id})")
    print("-" * 80)
    
    socios_ids = Acceso.objects.filter(sucursal=suc).values_list('socio_id', flat=True).distinct()
    
    dentro_suc = 0
    for sid in socios_ids:
        ultimo = Acceso.objects.filter(socio_id=sid, sucursal=suc).order_by('-fecha_hora').first()
        
        if ultimo.tipo == "Ingreso":
            socio = Socio.objects.get(id=sid)
            nombre = f"{socio.nombre} {socio.apellido}".strip() or socio.email or f"Socio #{sid}"
            print(f"   🟢 {nombre}")
            dentro_suc += 1
    
    if dentro_suc == 0:
        print("   (vacío)")
    
    print(f"   Subtotal: {dentro_suc} personas")
    total_dentro += dentro_suc

print(f"\n{'='*80}")
print(f"🎯 TOTAL GLOBAL: {total_dentro} personas dentro")
print(f"{'='*80}\n")
