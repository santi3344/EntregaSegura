from django.db import models
from django.contrib.auth.models import User


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