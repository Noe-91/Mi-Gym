from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Socio, Suscripcion, Plan
from .utils import can_access
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import SocioForm, SuscripcionForm

# Create your views here.

def eliminar_socio(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    nombre = socio.user.get_full_name() or socio.user.username
    socio.delete()
    messages.success(request, f"Se eliminó el socio {nombre}.")
    return redirect("socios:lista")

@login_required
def lista_socios(request):
    qs = Socio.objects.select_related("user", "sucursal")
    ape = request.GET.get("apellido", "").strip()
    if ape:
        qs = qs.filter(user__last_name__icontains=ape)
    return render(request, "socios/lista.html", {"socios": qs})

@login_required
def detalle_socio(request, pk):
    socio = get_object_or_404(Socio.objects.select_related("user", "sucursal"), pk=pk)
    suscripciones = Suscripcion.objects.filter(socio=socio).select_related("plan").order_by("-fecha_fin")
    # planes activos para el modal de 'Registrar pago'
    planes = Plan.objects.filter(activo=True).order_by("nombre")
    # si el socio tiene al menos una suscripción vigente
    activo = can_access(socio)
    return render(request, "socios/detalle.html", {"socio": socio, "suscripciones": suscripciones, "planes": planes, "has_active": activo})

@login_required
def crear_socio(request):
    if request.method == "POST":
        form = SocioForm(request.POST)
        if form.is_valid():
            socio = form.save()
            messages.success(request, "El socio se creó correctamente.")
            return redirect(f"{reverse('socios:detalle', args=[socio.pk])}?created=1")
        else:
            messages.error(request, "El socio ya se encuentra registrado.")
    else:
        form = SocioForm()
    return render(request, "socios/socio_form.html", {"form": form})

@login_required
def editar_socio(request, pk):
    from .forms import SocioEditForm  # importá el nuevo form

    socio = get_object_or_404(Socio, pk=pk)

    if request.method == "POST":
        form = SocioEditForm(request.POST, instance=socio)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Datos del socio actualizados correctamente.")
            return redirect("socios:detalle", pk=socio.pk)
        else:
            messages.error(request, "El socio ya se encuentra registrado.")
    else:
        form = SocioEditForm(instance=socio)

    return render(request, "socios/editar.html", {"form": form, "socio": socio})


@login_required
def crear_suscripcion(request, socio_id=None):
    initial = {"socio": socio_id} if socio_id else None
    if request.method == "POST":
        form = SuscripcionForm(request.POST)
        if form.is_valid():
            sus = form.save()
            # Si venimos con ?to_pagos=1 redirigimos al formulario de Pago
            if request.GET.get("to_pagos") == "1":
                return redirect(f"{reverse('pagos:pagos_crear')}?suscripcion={sus.pk}")

            return redirect("socios:detalle", pk=form.cleaned_data["socio"].pk)
    else:
        form = SuscripcionForm(initial=initial)
    planes = Plan.objects.filter(activo=True).order_by("nombre")
    return render(request, "socios/form_suscripcion.html", {"form": form, "planes": planes})


@login_required
def suscripciones_pendientes(request):
    """Lista todas las suscripciones en estado 'Pendiente' (pendientes de pago)."""
    qs = Suscripcion.objects.filter(estado="Pendiente").select_related("socio", "plan").order_by("socio__apellido", "socio__nombre")
    return render(request, "socios/suscripciones_pendientes.html", {"suscripciones": qs})


@login_required
def crear_suscripcion_rapida(request):
    """Crea una Suscripcion en estado 'Pendiente' a partir de un POST desde el modal.

    Espera campos POST: socio_id, plan_id, monto (opcional).
    Redirige a la vista de crear pago con ?suscripcion=<id>.
    """
    if request.method != "POST":
        return redirect("socios:lista")

    socio_id = request.POST.get("socio_id")
    plan_id = request.POST.get("plan_id")
    monto = request.POST.get("monto")

    # validaciones mínimas
    try:
        socio = Socio.objects.get(pk=int(socio_id))
    except Exception:
        messages.error(request, "Socio inválido")
        return redirect("socios:detalle", pk=socio_id)

    try:
        plan = Plan.objects.get(pk=int(plan_id))
    except Exception:
        messages.error(request, "Plan inválido")
        return redirect("socios:detalle", pk=socio_id)

    # monto por defecto desde el plan si no se provee
    if not monto:
        monto_value = plan.precio
    else:
        try:
            from decimal import Decimal
            monto_value = Decimal(monto)
        except Exception:
            monto_value = plan.precio

    # Antes de crear, comprobamos que no exista ya una suscripción vigente
    from django.utils import timezone
    hoy = timezone.localdate()
    existe_vigente = Suscripcion.objects.filter(socio=socio, estado="Vigente", fecha_inicio__lte=hoy, fecha_fin__gte=hoy).exists()
    if existe_vigente:
        from django.contrib import messages
        messages.error(request, "El socio ya tiene una suscripción vigente. No se creó una nueva suscripción.")
        return redirect("socios:detalle", pk=socio.pk)

    sus = Suscripcion.objects.create(
        socio=socio,
        plan=plan,
        monto=monto_value,
        estado="Pendiente",
    )

    return redirect(f"{reverse('pagos:pagos_crear')}?suscripcion={sus.pk}")