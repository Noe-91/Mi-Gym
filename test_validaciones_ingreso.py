"""
Script para probar las validaciones de ingreso:
1. Socio desactivado
2. Suscripción vencida
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migym_registro.settings.local')
django.setup()

from aplications.socios.models import Socio, Suscripcion
from django.utils import timezone

print("=" * 60)
print("VERIFICANDO VALIDACIONES DE INGRESO")
print("=" * 60)

# 1. Verificar socios desactivados
socios_desactivados = Socio.objects.filter(activo=False)
print(f"\n1. Socios DESACTIVADOS: {socios_desactivados.count()}")
for socio in socios_desactivados[:5]:
    print(f"   - {socio.nombre} {socio.apellido} ({socio.email}) - DNI: {socio.dni}")

# 2. Verificar suscripciones vencidas
suscripciones_vencidas = Suscripcion.objects.filter(estado="Vencida")
print(f"\n2. Suscripciones VENCIDAS: {suscripciones_vencidas.count()}")
for susc in suscripciones_vencidas[:5]:
    socio = susc.socio
    print(f"   - {socio.nombre} {socio.apellido} ({socio.email})")
    print(f"     Plan: {susc.plan.nombre} | Fin: {susc.fecha_fin}")

# 3. Socios activos sin suscripción vigente
print(f"\n3. Socios ACTIVOS sin suscripción vigente:")
socios_activos = Socio.objects.filter(activo=True)
count = 0
for socio in socios_activos[:10]:
    susc_vigente = Suscripcion.objects.filter(socio=socio, estado="Vigente").exists()
    if not susc_vigente:
        count += 1
        print(f"   - {socio.nombre} {socio.apellido} ({socio.email})")

print(f"\nTotal socios activos sin suscripción vigente: {count}")

print("\n" + "=" * 60)
print("RESUMEN:")
print(f"- Socios desactivados: {socios_desactivados.count()}")
print(f"- Suscripciones vencidas: {suscripciones_vencidas.count()}")
print(f"- Socios activos sin suscripción: {count}")
print("=" * 60)
