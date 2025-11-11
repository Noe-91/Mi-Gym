# Sistema de Acceso con Código QR - MiGym

## 🎯 Funcionalidad

Sistema completo de acceso al gimnasio usando códigos QR personalizados para cada socio.

## 📋 Características

### 1. Panel del Socio - Mi QR
- Cada socio tiene su código QR único generado automáticamente
- Basado en su email (identificador único)
- Puede ver y descargar su QR desde el panel
- Diseño minimalista acorde al theme

### 2. Simulador de Acceso Mejorado
- **Modo Manual**: Ingreso de email tradicional
- **Modo QR**: Escaneo de código QR con cámara
- Interfaz web moderna y responsiva
- Log de accesos en tiempo real
- Switch fácil entre modos

## 🚀 Uso

### Para el Socio:
1. Iniciar sesión en el panel
2. Ir a "Mi QR" en el menú lateral
3. Ver su código QR personalizado
4. Opcionalmente descargarlo en formato PNG
5. Mostrar el QR al ingresar al gym

### Para el Administrador/Recepción:
1. Abrir el simulador: `tools/simulador_qr.html` en un navegador
2. Asegurarse que el servidor Django esté corriendo
3. Elegir método de registro:
   - **Manual**: Escribir email y presionar "Registrar Acceso"
   - **QR**: Click en "Escanear QR" y colocar código frente a la cámara
4. Ver confirmación en el log de accesos

## 🔧 Configuración

### Requisitos
```bash
# Librerías Python ya instaladas
pip install qrcode[pil] opencv-python
```

### API Endpoint
```
POST http://localhost:8000/aplicaciones/ocupacion/api/access/
Headers:
  - X-Device-Token: secret-token-123
  - Content-Type: application/json

Body:
{
  "member_code": "socio@email.com",
  "type": "IN",
  "source": "RFID",
  "raw_uid": "socio@email.com",
  "device_id": "kiosk-sim-1"
}
```

## 📱 URLs Agregadas

```python
# Panel del Socio
path("panel/mi-qr/", views.mi_qr, name="mi_qr")
```

## 🎨 Diseño

### Panel del Socio - Mi QR
- Card minimalista con borde y sombra
- Código QR con fondo blanco y padding
- Info del socio y sucursal
- Botón de descarga
- Instrucciones de uso

### Simulador
- Tema oscuro acorde a MiGym
- Tabs para cambiar entre métodos
- Scanner QR con html5-qrcode
- Log de eventos con timestamps
- Responsive design

## 🔐 Seguridad

- QR contiene solo el email del socio
- Validación en backend contra base de datos
- Token de dispositivo para API
- QR personal e intransferible

## 📊 Flujo de Datos

```
Socio accede a "Mi QR"
    ↓
Vista genera QR (base64)
    ↓
Socio muestra QR en recepción
    ↓
Simulador escanea QR
    ↓
Extrae email del QR
    ↓
POST a /api/access/
    ↓
Backend registra Ingreso/Egreso
    ↓
Actualiza ocupación en tiempo real
```

## 🧪 Testing

1. **Generar QR**:
   ```
   - Login como socio
   - Ir a "Mi QR"
   - Verificar que aparece el código
   ```

2. **Escanear QR**:
   ```
   - Abrir simulador_qr.html
   - Click en "Escanear QR"
   - Permitir acceso a cámara
   - Mostrar QR del socio
   - Verificar log de acceso
   ```

3. **Verificar Dashboard**:
   ```
   - Ir a dashboard admin
   - Ver ocupación actualizada
   - Confirmar que el socio aparece "dentro"
   ```

## 📝 Archivos Modificados/Creados

```
aplications/socios/
  ├── views.py (+ vista mi_qr)
  └── urls.py (+ path mi_qr)

templates/
  ├── socios/panel/mi_qr.html (nuevo)
  └── partials/sidebar_socio.html (+ enlace QR)

tools/
  └── simulador_qr.html (nuevo)
```

## 💡 Próximas Mejoras

- [ ] QR con timestamp para mayor seguridad
- [ ] Historial de accesos en panel del socio
- [ ] Notificaciones push al registrar acceso
- [ ] App móvil con QR integrado
- [ ] Estadísticas de uso del QR

## 🆘 Troubleshooting

**El QR no se genera:**
- Verificar que qrcode esté instalado: `pip list | grep qrcode`
- Revisar permisos del usuario

**La cámara no funciona:**
- Usar HTTPS o localhost
- Permitir acceso a cámara en el navegador
- Verificar que no esté en uso por otra app

**El simulador no registra:**
- Verificar que Django esté corriendo
- Confirmar URL de API en simulador_qr.html
- Revisar token de dispositivo

## 📞 Soporte

Para dudas o problemas, revisar logs del servidor Django y consola del navegador.
