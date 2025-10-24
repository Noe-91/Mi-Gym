from django.urls import path
from . import views

app_name = "socios"

urlpatterns = [
    path("", views.lista_socios, name="lista"),
    path("<int:pk>/", views.detalle_socio, name="detalle"),
    path("nuevo/", views.crear_socio, name="socios_crear"),
    path("<int:pk>/editar/", views.editar_socio, name="editar"),
    path("<int:socio_id>/suscripciones/nueva/", views.crear_suscripcion, name="suscripcion_crear"),
    path("suscripciones/pendientes/", views.suscripciones_pendientes, name="suscripciones_pendientes"),
    path("suscripciones/rapida/", views.crear_suscripcion_rapida, name="suscripcion_rapida"),
    path("<int:pk>/eliminar/", views.eliminar_socio, name="eliminar"),

]

