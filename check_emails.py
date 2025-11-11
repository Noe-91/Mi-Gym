import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migym_registro.settings.local')
django.setup()

from aplications.socios.models import Socio

# Buscar el socio
email_socio = 'noeliasramoss17@gmail.com'
socio = Socio.objects.get(email=email_socio)

print(f"\n{'='*60}")
print(f"Email en modelo Socio: {socio.email}")
print(f"Email en User asociado: {socio.user.email}")
print(f"Username del User: {socio.user.username}")
print(f"\nQR generado con: {socio.user.email}")
print(f"API busca por: email del payload")
print(f"{'='*60}\n")

if socio.email != socio.user.email:
    print("⚠️ LOS EMAILS NO COINCIDEN!")
    print(f"   Socio.email = {socio.email}")
    print(f"   User.email = {socio.user.email}")
    print("\n   El QR tiene un email diferente al del Socio")
else:
    print("✓ Los emails coinciden")
