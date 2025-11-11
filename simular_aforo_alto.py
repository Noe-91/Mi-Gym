"""
Script para simular aforo alto en sucursal Caballito-GYM
"""

import requests
import time

API_URL = "http://localhost:8000/ocupacion/api/access/"
DEVICE_TOKEN = "secret-token-123"

# Lista de emails de socios para simular ingresos
socios = [
    "andrés.gonzález1@email.com",
    "andrés.cruz2@email.com",
    "diego.flores3@email.com",
    "valentina.díaz4@email.com",
    "pedro.díaz5@email.com",
    "miguel.ramírez6@email.com",
    "luis.lópez7@email.com",
    "carolina.torres8@email.com",
    "juan.ramírez9@email.com",
    "sofía.garcía10@email.com",
    "martín.lópez11@email.com",
    "ana.martínez12@email.com",
    "pablo.fernández13@email.com",
    "lucía.rodríguez14@email.com",
    "santiago.pérez15@email.com"
]

print("=" * 60)
print("SIMULANDO AFORO ALTO EN CABALLITO-GYM")
print("=" * 60)

headers = {
    "Content-Type": "application/json",
    "X-Device-Token": DEVICE_TOKEN
}

ingresos_exitosos = 0
errores = 0

for email in socios:
    payload = {
        "member_code": email,
        "type": "IN",
        "source": "RFID",
        "raw_uid": email,
        "device_id": "kiosk-caballito-1",
        "sucursal_id": 1  # ID de Caballito-GYM
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            nombre = data.get("socio_nombre", email)
            print(f"✓ INGRESO: {nombre}")
            ingresos_exitosos += 1
        elif response.status_code == 403:
            data = response.json()
            print(f"✗ DENEGADO: {email} - {data.get('message', 'Error')}")
            errores += 1
        else:
            print(f"✗ ERROR: {email} - {response.status_code}")
            errores += 1
            
        time.sleep(0.3)  # Pequeña pausa entre ingresos
        
    except Exception as e:
        print(f"✗ ERROR DE CONEXIÓN: {email} - {e}")
        errores += 1

print("\n" + "=" * 60)
print(f"RESUMEN:")
print(f"- Ingresos exitosos: {ingresos_exitosos}")
print(f"- Errores: {errores}")
print("=" * 60)
