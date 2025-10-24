from django.core.management.base import BaseCommand
from django.utils import timezone

from aplications.socios.models import Suscripcion


class Command(BaseCommand):
    help = "Marca como 'Vencida' las suscripciones Vigentes cuya fecha_fin ya pasó."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="No modifica la base de datos, solo muestra lo que cambiaría.",
        )

    def handle(self, *args, **options):
        hoy = timezone.localdate()
        pendientes = Suscripcion.objects.filter(estado="Vigente", fecha_fin__lt=hoy)
        total = pendientes.count()
        if options.get("dry_run"):
            self.stdout.write(self.style.WARNING(f"[DRY-RUN] {total} suscripciones se marcarían como Vencida."))
            for s in pendientes:
                self.stdout.write(f"- {s.id} {s.socio} (fin={s.fecha_fin})")
            return

        self.stdout.write(f"Marcando {total} suscripciones como Vencida...")
        updated = pendientes.update(estado="Vencida")
        self.stdout.write(self.style.SUCCESS(f"Hecho. {updated} suscripciones actualizadas."))
