from django.db import models
from django.contrib.auth.models import User
import uuid


class Perfil(models.Model):

    ROLES = [
        ('ESTUDIANTE', 'Estudiante'),
        ('DOCENTE', 'Docente'),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    rol = models.CharField(
        max_length=20,
        choices=ROLES
    )

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"


class RegistroDocentePendiente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150)
    email = models.EmailField()
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    password_hash = models.CharField(max_length=128)
    codigo_hash = models.CharField(max_length=128)
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    intentos = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"Registro docente pendiente: {self.username}"