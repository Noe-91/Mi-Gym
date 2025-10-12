from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Socio, Suscripcion, Plan
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
    return render(request, "socios/detalle.html", {"socio": socio, "suscripciones": suscripciones})

@login_required
def crear_socio(request):
    if request.method == "POST":
        form = SocioForm(request.POST)
        if form.is_valid():
            socio = form.save()
            messages.success(request, "El socio se creó correctamente.")
            return redirect(f"{reverse('socios:detalle', args=[socio.pk])}?created=1")
    else:
        form = SocioForm()
    return render(request, "socios/socio_form.html", {"form": form})

@login_required
def editar_socio(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    if request.method == "POST":
        form = SocioForm(request.POST, instance=socio)
        if form.is_valid():
            form.save()
            return redirect("socios:detalle", pk=socio.pk)
    else:
        form = SocioForm(instance=socio)
    return render(request, "socios/form_socio.html", {"form": form})

@login_required
def crear_suscripcion(request, socio_id=None):
    initial = {"socio": socio_id} if socio_id else None
    if request.method == "POST":
        form = SuscripcionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("socios:detalle", pk=form.cleaned_data["socio"].pk)
    else:
        form = SuscripcionForm(initial=initial)
    planes = Plan.objects.filter(activo=True).order_by("nombre")
    return render(request, "socios/form_suscripcion.html", {"form": form, "planes": planes})



