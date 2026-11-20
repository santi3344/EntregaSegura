from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistroDocenteForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico')
    telefono = forms.CharField(
        label='Teléfono celular',
        max_length=16,
        help_text='Usa formato internacional, por ejemplo +573001234567.',
    )
    first_name = forms.CharField(label='Nombre', max_length=150)
    last_name = forms.CharField(label='Apellidos', max_length=150)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono')
        labels = {'username': 'Nombre de usuario'}

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not username:
            raise forms.ValidationError('El nombre de usuario es obligatorio.')
        if any(ord(char) < 32 for char in username):
            raise forms.ValidationError('El usuario contiene caracteres inválidos.')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está registrado.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean_first_name(self):
        value = self.cleaned_data['first_name'].strip()
        if not value:
            raise forms.ValidationError('El nombre es obligatorio.')
        if any(ord(char) < 32 for char in value):
            raise forms.ValidationError('El nombre contiene caracteres inválidos.')
        return value

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono'].strip()
        if not telefono.startswith('+') or not telefono[1:].isdigit():
            raise forms.ValidationError(
                'Ingresa el teléfono en formato internacional, por ejemplo +573001234567.'
            )
        if not 10 <= len(telefono[1:]) <= 15:
            raise forms.ValidationError('El teléfono debe tener entre 10 y 15 dígitos.')
        return telefono

    def clean_last_name(self):
        value = self.cleaned_data['last_name'].strip()
        if not value:
            raise forms.ValidationError('Los apellidos son obligatorios.')
        if any(ord(char) < 32 for char in value):
            raise forms.ValidationError('Los apellidos contienen caracteres inválidos.')
        return value