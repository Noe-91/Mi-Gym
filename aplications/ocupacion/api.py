from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from django.db import transaction
from aplications.socios.models import Socio
from .models import AccessEvent, ActiveSession, Acceso

# simple header token for device authentication
DEVICE_TOKENS = {"kiosk-1":"secret-token-123"}  # en prod: DB + rotate

def authenticate_device(request):
    token = request.headers.get("X-Device-Token")
    return token in DEVICE_TOKENS.values()

class CheckInOutAPIView(APIView):
    permission_classes = [permissions.AllowAny]  # device uses token header

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        body: { "member_code": "SOC123", "type":"IN"|"OUT", "source":"RFID", "raw_uid":"04A1B2C3", "device_id":"kiosk-1" }
        """
        if not authenticate_device(request):
            return Response({"detail":"invalid device token"}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        member_code = data.get("member_code")
        try:
            # Buscar por email que es el identificador único del socio
            socio = Socio.objects.get(email=member_code)
        except Socio.DoesNotExist:
            return Response({"detail":"member not found"}, status=status.HTTP_404_NOT_FOUND)

        source = data.get("source")
        device_id = data.get("device_id")
        raw_uid = data.get("raw_uid")
        request_type = data.get("type")  # Lo que envía el front (IGNORAR para QR)
        
        # Auto-detectar si debe ser IN o OUT según el último acceso registrado
        ultimo_acceso = Acceso.objects.filter(socio=socio).order_by('-fecha_hora').first()
        
        import sys
        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write(f"DEBUG QR - Payload recibido: {data}\n")
        sys.stdout.write(f"DEBUG QR - Type del request: {request_type} (SERÁ IGNORADO)\n")
        sys.stdout.write(f"DEBUG QR - Email buscado: {member_code}\n")
        sys.stdout.write(f"DEBUG QR - Socio encontrado: {socio.email}\n")
        sys.stdout.write(f"DEBUG QR - Último acceso: {ultimo_acceso.tipo if ultimo_acceso else 'NINGUNO'}\n")
        sys.stdout.write(f"DEBUG QR - Fecha último: {ultimo_acceso.fecha_hora if ultimo_acceso else 'N/A'}\n")
        sys.stdout.flush()
        
        if ultimo_acceso and ultimo_acceso.tipo == "Ingreso":
            # Último registro fue Ingreso, ahora debe ser Egreso
            atype = "OUT"
            tipo_registro = "Egreso"
            sys.stdout.write(f"DEBUG QR - ✓ Asignando: EGRESO (porque último fue Ingreso)\n")
        else:
            # No hay registros o último fue Egreso, ahora debe ser Ingreso
            atype = "IN"
            tipo_registro = "Ingreso"
            sys.stdout.write(f"DEBUG QR - ✓ Asignando: INGRESO (porque {('último fue Egreso' if ultimo_acceso else 'no hay registros')})\n")
        sys.stdout.write("="*60 + "\n\n")
        sys.stdout.flush()

        # register event
        AccessEvent.objects.create(member=socio, type=atype, source=source, device_id=device_id, raw_uid=raw_uid)
        
        # Registrar en tabla Acceso (el sistema principal)
        now = timezone.now()
        Acceso.objects.create(
            socio=socio,
            sucursal=socio.sucursal,
            tipo=tipo_registro,
            fecha_hora=now
        )

        # business rules:
        socio_nombre = socio.user.get_full_name() or socio.user.username
        
        # Actualizar ActiveSession para ocupación
        if atype == "IN":
            session, created = ActiveSession.objects.get_or_create(member=socio, defaults={"check_in_at": now})
            session.status = "ACTIVE"
            session.check_in_at = now
            session.check_out_at = None
            session.save()
            mensaje = "Ingreso registrado"
        else:  # OUT
            try:
                session = ActiveSession.objects.get(member=socio, status="ACTIVE")
                session.check_out_at = now
                session.status = "CLOSED"
                session.save()
            except ActiveSession.DoesNotExist:
                pass  # No hay sesión activa, pero igual registramos el egreso
            mensaje = "Egreso registrado"

        # publish occupancy update (see function abajo)
        #publish_occupancy_update()

        return Response({
            "status": "ok",
            "message": mensaje,
            "socio_nombre": socio_nombre,
            "tipo": atype,
            "tipo_registro": tipo_registro
        }, status=status.HTTP_200_OK)
