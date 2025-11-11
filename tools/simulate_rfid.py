# tools/simulate_rfid.py
import requests 
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--api", default="http://localhost:8000/aplicaciones/ocupacion/api/access/")
parser.add_argument("--device", default="kiosk-sim-1")
parser.add_argument("--token", default="secret-token-123")
parser.add_argument("--source", default="RFID")
args = parser.parse_args()

headers = {"X-Device-Token": args.token, "Content-Type": "application/json"}

print("Simulador RFID. Pegá el UID o escribí 'rand' para UID aleatorio. Ctrl+C para salir.")
import uuid
while True:
    try:
        uid = input("UID> ").strip()
        if not uid:
            continue
        if uid.lower() == "rand":
            uid = uuid.uuid4().hex[:8].upper()
        # en muchos setups la tarjeta tiene map a member_code (ej: tabla card_uid -> socio)
        # para el ejemplo, asumimos member_code = UID (o definir mapping local)
        payload_in = {
            "member_code": uid,   # si tu Socio.code es distinto, ajustar
            "type": "IN",
            "source": args.source,
            "raw_uid": uid,
            "device_id": args.device
        }
        r = requests.post(args.api, json=payload_in, headers=headers)
        if r.status_code == 403:
            try:
                error_data = r.json()
                print(f"❌ ACCESO DENEGADO: {error_data.get('message', '')}")
                print(f"   {error_data.get('detail', '')}")
            except:
                print("IN ->", r.status_code, r.text)
        else:
            print("IN ->", r.status_code, r.text)
        time.sleep(1)
        payload_out = payload_in.copy()
        payload_out["type"] = "OUT"
        # opcional: simular salida más tarde
        # r = requests.post(args.api, json=payload_out, headers=headers)
        # print("OUT ->", r.status_code, r.text)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print("Error:", e)
