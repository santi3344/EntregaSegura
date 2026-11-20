from django.db import models
from django.contrib.auth.models import User


class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    docente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cursos'
    )

    def __str__(self):
        return self.nombre


class Grupo(models.Model):
    nombre = models.CharField(max_length=50)
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='grupos'
    )
    estudiantes = models.ManyToManyField(
        'usuarios.Perfil',
        blank=True,
        related_name='grupos',
        limit_choices_to={'rol': 'ESTUDIANTE'},
    )

    def __str__(self):
        return f"{self.curso.nombre} - {self.nombre}"