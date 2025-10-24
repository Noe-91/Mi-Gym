# Gestión de Suscripciones - MiGym Registro

El sistema MiGym Registro permite administrar las suscripciones de los socios del gimnasio en función de los planes configurados previamente por el administrador.
Cada suscripción se crea automáticamente al registrar un pago, y su vigencia se calcula en base a la duración establecida en el plan seleccionado.

## 1. Configuración de Planes

Antes de registrar pagos, el administrador define los planes disponibles en el sistema.
Cada plan incluye los siguientes datos:

- **Nombre del plan:** Ejemplo: “Mensual”, “Quincenal”, “Anual”.
- **Duración (en días):** Número de días que durará la suscripción.
- **Precio:** Importe correspondiente al plan.
- **Estado:** Activo o inactivo.

## 2. Registro de Pagos y Creación de Suscripciones

Cuando un socio realiza un pago:

1. El administrador selecciona el socio y el plan correspondiente.
2. El sistema registra el pago y crea automáticamente una suscripción con estado **ACTIVA**.
3. Se asignan las fechas:
   - **Fecha de inicio:** coincide con la fecha del pago.
   - **Fecha de fin:** se calcula sumando la duración del plan (por ejemplo, 30 días).

> Nota: En la implementación actual las suscripciones pueden crearse inicialmente en estado **Pendiente** (sin fechas). Al registrar el `Pago` asociado, una señal activa la suscripción y fija las fechas.

## 3. Control de Acceso

El sistema de control de acceso (por QR o tarjeta) permite ingresar solo a los socios con una suscripción **ACTIVA** y vigente, es decir, cuya fecha actual se encuentre entre la fecha de inicio y la fecha de fin.
Si la suscripción está vencida, el ingreso será denegado automáticamente.

## 4. Vencimiento y Renovación

Al llegar la fecha de fin, la suscripción cambia automáticamente al estado **VENCIDA**.

Para volver a ingresar al gimnasio, el socio debe realizar un nuevo pago, lo que generará una nueva suscripción **ACTIVA** según el plan elegido.

## 5. Estados de la Suscripción

| Estado   | Descripción                                  | Acceso permitido |
|----------|----------------------------------------------|------------------|
| Activa   | Pago registrado y dentro del período         | ✅ Sí             |
| Vencida  | Finalizó la vigencia, no hay nuevo pago      | ❌ No             |

## 6. Reglas Principales

- La suscripción solo se crea al registrarse un pago válido (o en estado pendiente hasta el pago).
- La vigencia se calcula automáticamente según la duración del plan.
- No se permite acceso sin una suscripción activa y vigente.
- Al vencer la suscripción, el acceso se bloquea hasta registrar un nuevo pago.

---

Implementación técnica (resumen):

- Modelos relevantes: `aplications.socios.Plan`, `aplications.socios.Suscripcion`, `aplications.pagos.Pago`.
- Al crear un `Pago`, una señal `post_save` activa la `Suscripcion` asociada (método `Suscripcion.activate`) y fija `fecha_inicio`/`fecha_fin`.
- Hay un comando de management `python manage.py expire_subscriptions` que marca como `Vencida` las suscripciones cuyo `fecha_fin` ya pasó.
- Utilidad para control de acceso: `aplications.socios.utils.can_access(socio)`.

Si querés, puedo también añadir este documento al `README.md` principal o generar una versión en inglés.
