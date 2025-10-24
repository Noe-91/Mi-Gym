from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PagoForm

# Create your views here.

@login_required
def crear_pago(request):
    if request.method == "POST":
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save()
            socio_id = pago.suscripcion.socio_id
            return redirect("socios_detalle", pk=socio_id)
    else:
        # allow prefilling suscripcion via GET param ?suscripcion=<id>
        initial = {}
        sus_id = request.GET.get("suscripcion")
        if sus_id:
            initial["suscripcion"] = sus_id
        form = PagoForm(initial=initial)
    return render(request, "pagos/form_pago.html", {"form": form})

@login_required
def listar_pagos(request):
    from .models import Pago
    pagos = Pago.objects.select_related("suscripcion", "suscripcion__socio", "suscripcion__plan").order_by("-fecha_pago")
    return render(request, "pagos/lista.html", {"pagos": pagos})
