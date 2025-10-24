from django.utils import timezone


def can_access(socio) -> bool:
    """Devuelve True si el socio tiene al menos una suscripción activa (Vigente)

    y la fecha actual está dentro del período (fecha_inicio <= hoy <= fecha_fin).
    """
    hoy = timezone.localdate()
    sus = (
        socio.suscripciones.filter(estado="Vigente")
        .filter(fecha_inicio__lte=hoy, fecha_fin__gte=hoy)
        .order_by("-fecha_fin")
        .first()
    )
    return sus is not None
