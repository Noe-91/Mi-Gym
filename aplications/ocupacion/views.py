from django.contrib.auth.decorators import login_required
from django.db.models import Subquery, OuterRef, Count, Sum, Value, IntegerField
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .forms import AccesoForm
from .models import Acceso
from aplications.socios.models import Sucursal, Socio 

from django.db.models.functions import Coalesce 
# ---------------------------
# Alta manual con formulario
# ---------------------------
@login_required
def registrar_acceso(request):
    if request.method == "POST":
        form = AccesoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("ocupacion:ocupacion_actual")  # usa namespace si lo tenés
    else:
        form = AccesoForm()
    return render(request, "ocupacion/form_acceso.html", {"form": form})

# --------------------------------------
# Vista HTML para ver ocupación por sede
# --------------------------------------
@login_required
def ocupacion_actual(request):
    """
    Lógica: por cada socio en cada sucursal, tomamos su último movimiento.
    Si el último es 'Ingreso' => está adentro.
    Optimizado con Subquery (evita N+1 queries).
    """
    # Subconsulta: para cada (socio, sucursal), traemos el TIPO del último movimiento
    ultimo_tipo_subq = (
        Acceso.objects
        .filter(socio_id=OuterRef("socio_id"), sucursal_id=OuterRef("sucursal_id"))
        .order_by("-fecha_hora")
        .values("tipo")[:1]
    )

    # Filtramos solo los casos cuyo último movimiento fue 'Ingreso'
    ultimos_ingreso = (
        Acceso.objects
        .values("socio_id", "sucursal_id")
        .distinct()
        .annotate(ultimo_tipo=Subquery(ultimo_tipo_subq))
        .filter(ultimo_tipo="Ingreso")
    )

    # Conteo por sucursal
    conteo_por_sucursal = (
        ultimos_ingreso
        .values("sucursal_id")
        .annotate(dentro=Count("socio_id"))
    )
    dentro_map = {row["sucursal_id"]: row["dentro"] for row in conteo_por_sucursal}

    # Armamos respuesta para cada sucursal
    data = []
    for s in Sucursal.objects.all():
        occ = dentro_map.get(s.id, 0)
        cap = getattr(s, "aforo_maximo", None) or 0
        pct = (occ * 100.0 / cap) if cap else 0.0

        # Umbrales (asumimos que existen en Sucursal; si no, fijá valores por defecto)
        low = getattr(s, "umbral_bajo_pct", 33)
        mid = getattr(s, "umbral_medio_pct", 66)

        if pct <= low:
            leyenda = "Baja"
        elif pct <= mid:
            leyenda = "Media"
        else:
            leyenda = "Alta"

        data.append({"sucursal": s, "ocupacion": occ, "capacidad": cap, "porcentaje": round(pct, 1), "leyenda": leyenda})

    return render(request, "ocupacion/actual.html", {"items": data})

# ---------------------------
# Página del simulador visual
# ---------------------------
@login_required
def simulador(request):
    return render(request, "ocupacion/simulador.html")

def simulador_qr(request):
    """Simulador con escáner QR"""
    return render(request, "ocupacion/simulador_qr.html")

# -------------------------------------------------------------------
# API para el simulador: registrar IN/OUT y consultar ocupación actual
# (Django puro, sin DRF; si usás DRF, lo migramos fácil más adelante)
# -------------------------------------------------------------------

@csrf_exempt
def access_event(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    import json, traceback
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"detail": "invalid json"}, status=400)

    member_code = data.get("member_code")
    atype = data.get("type")  # IN / OUT
    sucursal_id = data.get("sucursal_id")

    if not member_code or atype not in ("IN", "OUT"):
        return JsonResponse({"detail": "member_code y type son obligatorios (IN/OUT)"}, status=400)

    # 1) Buscar socio por DNI, username o email (para QR)
    from aplications.socios.models import Socio, Sucursal
    socio = None
    
    # Intentar por email primero (para QR)
    if '@' in member_code:
        socio = Socio.objects.filter(email=member_code).first()
    
    # Si no, intentar por DNI
    if not socio:
        try:
            socio = Socio.objects.get(dni=member_code)
        except Socio.DoesNotExist:
            # Finalmente por username
            try:
                socio = Socio.objects.get(user__username=member_code)
            except Socio.DoesNotExist:
                return JsonResponse({"detail": "member not found (email/dni/username)"}, status=404)

    # 2) Resolver sucursal
    sucursal = None
    if sucursal_id:
        sucursal = Sucursal.objects.filter(pk=sucursal_id).first()
    if not sucursal:
        sucursal = getattr(socio, "sucursal", None) or Sucursal.objects.first()
    if not sucursal:
        return JsonResponse({"detail": "no hay sucursal disponible (creá una en /admin)"}, status=400)

    # 3) AUTO-DETECTAR tipo según último acceso (para QR) - PRIMERO ANTES DE VALIDAR
    from django.utils import timezone
    from .models import Acceso, ActiveSession
    
    # Si la fuente es QR, ignorar el type del request y auto-detectar
    source = data.get("source", "")
    if source == "QR":
        ultimo_acceso = Acceso.objects.filter(socio=socio).order_by('-fecha_hora').first()
        if ultimo_acceso and ultimo_acceso.tipo == "Ingreso":
            tipo = "Egreso"
            atype = "OUT"
        else:
            tipo = "Ingreso"
            atype = "IN"
    else:
        # Para RFID y otros, usar el type del request
        tipo = "Ingreso" if atype == "IN" else "Egreso"
    
    # 3.1) VALIDACIONES DE INGRESO - Solo para ingresos (IN) - DESPUÉS DE AUTO-DETECTAR
    if atype == "IN":
        # Validar si el socio está desactivado
        if not socio.activo:
            return JsonResponse({
                "status": "error",
                "message": "SOCIO DESACTIVADO",
                "detail": "Tu membresía está desactivada. Por favor, presentate en recepción para más información."
            }, status=403)
        
        # Validar si tiene suscripción vencida
        from aplications.socios.models import Suscripcion
        
        # Buscar suscripción vigente
        suscripcion_vigente = Suscripcion.objects.filter(
            socio=socio,
            estado="Vigente"
        ).first()
        
        if not suscripcion_vigente:
            # Verificar si tiene alguna suscripción vencida
            suscripcion_vencida = Suscripcion.objects.filter(
                socio=socio,
                estado="Vencida"
            ).exists()
            
            if suscripcion_vencida:
                mensaje = "SUSCRIPCIÓN VENCIDA"
                detalle = "Tu suscripción ha vencido. Por favor, presentate en recepción para renovar tu membresía."
            else:
                mensaje = "SIN SUSCRIPCIÓN ACTIVA"
                detalle = "No tienes una suscripción activa. Por favor, presentate en recepción."
            
            return JsonResponse({
                "status": "error",
                "message": mensaje,
                "detail": detalle
            }, status=403)
    
    # 4) Crear movimiento en Acceso
    try:
        now = timezone.now()
        Acceso.objects.create(
            socio=socio,
            sucursal=sucursal,
            tipo=tipo,
            fecha_hora=now
        )
        
        # 5) Actualizar ActiveSession (para que occupancy_current funcione igual que el simulador original)
        if atype == "IN":
            session, created = ActiveSession.objects.get_or_create(
                member=socio, 
                defaults={"check_in_at": now}
            )
            session.status = "ACTIVE"
            session.check_in_at = now
            session.check_out_at = None
            session.save()
        else:  # OUT
            try:
                session = ActiveSession.objects.get(member=socio, status="ACTIVE")
                session.check_out_at = now
                session.status = "CLOSED"
                session.save()
            except ActiveSession.DoesNotExist:
                pass  # No hay sesión activa
        
        return JsonResponse({
            "status": "ok",
            "socio_nombre": socio.user.get_full_name() or socio.nombre,
            "tipo_registro": tipo
        })
    except Exception as e:
        # Log y respuesta clara
        traceback.print_exc()
        return JsonResponse({"detail": f"server error: {e}"}, status=500)




def occupancy_current(request):
    """
    Devuelve ocupación y capacidad.
    - ?sucursal_id=1 -> cuenta y capacidad de esa sucursal
    - sin sucursal_id -> cuenta total y capacidad total (suma de aforos)
    Respuesta: { "count": N, "capacity": M, "sucursal_id": "..." }
    
    Usa ActiveSession como el simulador original.
    """
    from .models import ActiveSession
    
    sucursal_id = request.GET.get("sucursal_id")

    # Contar sesiones activas
    active_sessions = ActiveSession.objects.filter(status="ACTIVE")
    
    if sucursal_id:
        # Filtrar por sucursal del socio
        active_sessions = active_sessions.filter(member__sucursal_id=sucursal_id)
    
    count = active_sessions.count()

    # ---- capacidad ----
    # Si viene sucursal_id: devolver aforo de esa sucursal
    # Si no: sumar aforo de todas
    from aplications.socios.models import Sucursal

    if sucursal_id:
        suc = Sucursal.objects.filter(pk=sucursal_id).values("aforo_maximo").first()
        capacity = int((suc or {}).get("aforo_maximo") or 0)
    else:
        agg = Sucursal.objects.aggregate(
            total=Coalesce(Sum("aforo_maximo"), Value(0, output_field=IntegerField()))
        )
        capacity = int(agg["total"] or 0)

    return JsonResponse({
        "count": count,
        "capacity": capacity,
        "sucursal_id": sucursal_id or None,
    })
