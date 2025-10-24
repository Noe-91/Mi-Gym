from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta, date

User = settings.AUTH_USER_MODEL


class Sucursal(models.Model):
    nombre = models.CharField(max_length=80)
    direccion = models.CharField(max_length=150)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=120, blank=True)
    aforo_maximo = models.PositiveIntegerField(default=100, validators=[MinValueValidator(1)])
    umbral_bajo_pct = models.PositiveSmallIntegerField(default=40, validators=[MinValueValidator(0), MaxValueValidator(100)])
    umbral_medio_pct = models.PositiveSmallIntegerField(default=70, validators=[MinValueValidator(0), MaxValueValidator(100)])
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"

    def __str__(self):
        return self.nombre 



class Socio(models.Model):
    dni_validator = RegexValidator(
        r"^\d{7,10}$",
        message="El DNI debe contener solo números (7 a 10 dígitos)."
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="perfil_socio"
    )

    nombre = models.CharField(max_length=100, default="")
    apellido = models.CharField(max_length=100, default="")
    email = models.EmailField(unique=True, default="")
    dni = models.CharField(
        max_length=20,
        unique=True,
        validators=[dni_validator],
        help_text="Este será tu usuario para iniciar sesión."
    )

    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, max_length=100)
    estado = models.CharField(max_length=20, default="Activo")
    fecha_alta = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.dni})"


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="instructor")
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name="instructores")
    especialidad = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Instructor"
        verbose_name_plural = "Instructores"

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Plan(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=200, blank=True)
    duracion_dias = models.PositiveIntegerField(validators=[MinValueValidator(1)]) 
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    requiere_certificado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"

    def __str__(self):
        return self.nombre


class Suscripcion(models.Model):
    # Añadimos el estado 'Pendiente' para representar suscripciones creadas pero no pagadas.
    ESTADOS = [
        ("Pendiente", "Pendiente de pago"),
        ("Vigente", "Vigente"),
        ("Vencida", "Vencida"),
        ("Pausada", "Pausada"),
        ("Cancelada", "Cancelada"),
    ]

    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name="suscripciones")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="suscripciones")
    # Permitir fechas nulas para poder crear la suscripción en estado Pendiente
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="Pendiente")
    auto_renovacion = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["socio", "fecha_fin"]),
            models.Index(fields=["estado"]),
        ]
        verbose_name = "Suscripción"
        verbose_name_plural = "Suscripciones"

    def __str__(self):
        return f"{self.socio} - {self.plan} ({self.fecha_inicio}→{self.fecha_fin})"

    def activate(self, start_date: date | None = None):
        """Activa la suscripción a partir de start_date (o hoy si no se provee).

        Calcula `fecha_fin` usando `plan.duracion_dias` y cambia el `estado` a 'Vigente'.
        La fecha de fin se calcula como fecha_inicio + duracion_dias - 1 (periodo inclusive).
        """
        if start_date is None:
            start_date = timezone.localdate()

        # Establecer fecha inicio y fin
        self.fecha_inicio = start_date
        try:
            days = int(self.plan.duracion_dias)
        except Exception:
            days = 0

        if days > 0:
            self.fecha_fin = self.fecha_inicio + timedelta(days=days - 1)
        else:
            self.fecha_fin = self.fecha_inicio

        self.estado = "Vigente"
        self.save(update_fields=["fecha_inicio", "fecha_fin", "estado"])