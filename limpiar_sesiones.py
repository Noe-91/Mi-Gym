import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migym_registro.settings.local')
django.setup()

from aplications.ocupacion.models import ActiveSession

# Ver todas las sesiones activas
print("\n" + "="*70)
print("SESIONES ACTIVAS ACTUALES")
print("="*70)

active = ActiveSession.objects.filter(status="ACTIVE")
print(f"Total sesiones activas: {active.count()}")

for session in active:
    print(f"  - {session.member.nombre} {session.member.apellido} (Sucursal: {session.member.sucursal.nombre})")

# Cerrar TODAS las sesiones activas
print("\n" + "="*70)
print("CERRANDO TODAS LAS SESIONES...")
print("="*70)

count = active.update(status="CLOSED")
print(f"✓ {count} sesiones cerradas")

print("\n" + "="*70)
print("VERIFICACIÓN FINAL")
print("="*70)
active_after = ActiveSession.objects.filter(status="ACTIVE").count()
print(f"Sesiones activas restantes: {active_after}")
print("="*70 + "\n")
