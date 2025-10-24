from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Pago


@receiver(post_save, sender=Pago)
def activar_suscripcion_al_pagar(sender, instance: Pago, created, **kwargs):
    """Cuando se registra un Pago nuevo, activamos la suscripción asociada.

    - Si la suscripción está en estado 'Pendiente' o diferente de 'Vigente', se activa.
    - La fecha de inicio será la fecha del pago (localdate).
    """
    if not created:
        return

    pago = instance
    sus = pago.suscripcion
    if not sus:
        return

    # Usamos la fecha del pago como inicio (fecha local)
    try:
        fecha_inicio = pago.fecha_pago.astimezone(timezone.get_current_timezone()).date()
    except Exception:
        fecha_inicio = timezone.localdate()

    # Activar la suscripción (método definido en el modelo Suscripcion)
    try:
        sus.activate(start_date=fecha_inicio)
    except Exception:
        # evitar que la señal falle ruidosamente; el admin puede ver el pago
        pass
