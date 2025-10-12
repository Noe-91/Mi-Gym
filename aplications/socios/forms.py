from django import forms
from django.contrib.auth.models import User
from .models import Socio, Suscripcion


# =======================
# Crear socio
# =======================
class SocioForm(forms.ModelForm):
    # datos del User (obligatorios)
    nombre   = forms.CharField(label="Nombre",  max_length=150, required=True)
    apellido = forms.CharField(label="Apellido", max_length=150, required=True)
    email    = forms.EmailField(label="Email", required=True)

    class Meta:
        model = Socio
        fields = ["dni", "sucursal", "estado", "nombre", "apellido", "email"]
        widgets = {
            "dni": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "DNI",
                "inputmode": "numeric",
                "pattern": r"[0-9]*",
                "required": "required",
            }),
            "sucursal": forms.Select(attrs={"class": "form-select", "required": "required"}),
            "estado": forms.Select(attrs={"class": "form-select", "required": "required"}),
        }
        labels = {"dni": "DNI", "sucursal": "Sucursal", "estado": "Estado"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nombre"].widget.attrs.update({"class": "form-control", "placeholder": "Nombre", "required": "required"})
        self.fields["apellido"].widget.attrs.update({"class": "form-control", "placeholder": "Apellido", "required": "required"})
        self.fields["email"].widget.attrs.update({"class": "form-control", "placeholder": "Email", "required": "required"})
        # refuerzo en backend
        self.fields["dni"].required = True
        self.fields["sucursal"].required = True
        self.fields["estado"].required = True

    def clean_dni(self):
        dni = str(self.cleaned_data.get("dni", "")).strip()
        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números.")
        if not (7 <= len(dni) <= 10):
            raise forms.ValidationError("El DNI debe tener entre 7 y 10 dígitos.")
        return dni

    def save(self, commit=True):
        """Crea el User con username = DNI y SIN contraseña usable (Opción A)."""
        socio = super().save(commit=False)

        first_name = self.cleaned_data["nombre"].strip()
        last_name  = self.cleaned_data["apellido"].strip()
        email      = self.cleaned_data["email"].strip()
        username   = self.cleaned_data["dni"].strip()  # login por DNI

        # crear usuario sin password utilizable (el usuario luego hará 'olvidé mi contraseña')
        user = User.objects.create_user(username=username, email=email)
        user.set_unusable_password()
        user.first_name = first_name
        user.last_name  = last_name
        user.save()

        socio.user = user
        if commit:
            socio.save()
        return socio


# =======================
# Editar socio
# =======================
class SocioEditForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombre",  max_length=150, required=True)
    last_name  = forms.CharField(label="Apellido", max_length=150, required=True)
    email      = forms.EmailField(label="Email", required=True)

    class Meta:
        model = Socio
        fields = ["dni", "sucursal", "estado", "first_name", "last_name", "email"]
        widgets = {
            "dni": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "DNI",
                "inputmode": "numeric",
                "pattern": r"[0-9]*",
                "required": "required",
            }),
            "sucursal": forms.Select(attrs={"class": "form-select", "required": "required"}),
            "estado": forms.Select(attrs={"class": "form-select", "required": "required"}),
        }
        labels = {"dni": "DNI", "sucursal": "Sucursal", "estado": "Estado"}

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        if instance and instance.user:
            self.fields["first_name"].initial = instance.user.first_name
            self.fields["last_name"].initial  = instance.user.last_name
            self.fields["email"].initial      = instance.user.email

        self.fields["first_name"].widget.attrs.update({"class": "form-control", "placeholder": "Nombre", "required": "required"})
        self.fields["last_name"].widget.attrs.update({"class": "form-control", "placeholder": "Apellido", "required": "required"})
        self.fields["email"].widget.attrs.update({"class": "form-control", "placeholder": "Email", "required": "required"})

        self.fields["dni"].required = True
        self.fields["sucursal"].required = True
        self.fields["estado"].required = True

    def clean_dni(self):
        dni = str(self.cleaned_data.get("dni", "")).strip()
        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números.")
        if not (7 <= len(dni) <= 10):
            raise forms.ValidationError("El DNI debe tener entre 7 y 10 dígitos.")
        return dni

    def save(self, commit=True):
        socio = super().save(commit=False)
        if commit:
            socio.save()
        if socio.user_id:
            u = socio.user
            u.first_name = self.cleaned_data.get("first_name", u.first_name)
            u.last_name  = self.cleaned_data.get("last_name",  u.last_name)
            u.email      = self.cleaned_data.get("email",      u.email)
            u.save()
        return socio


# =======================
# Suscripción
# =======================
class SuscripcionForm(forms.ModelForm):
    class Meta:
        model = Suscripcion
        fields = ["socio", "plan", "fecha_inicio", "fecha_fin", "monto", "estado", "auto_renovacion"]
