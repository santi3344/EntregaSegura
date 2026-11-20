from django.contrib.auth.models import User
from django.db import models

from cursos.models import Curso
from usuarios.models import Perfil


class Actividad(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='actividades'
    )
    fecha_limite = models.DateTimeField()
    creado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='actividades_creadas'
    )
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_limite']

    def __str__(self):
        return f'{self.titulo} ({self.curso})'


class Entrega(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('ENTREGADA', 'Entregada'),
        ('REVISADA', 'Revisada'),
        ('REENTREGADA', 'Reentregada'),
        ('CALIFICADA', 'Calificada'),
    ]

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='entregas'
    )
    estudiante = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='entregas'
    )
    archivo = models.FileField(upload_to='entregas/originales/%Y/%m/%d/')
    repositorio_github = models.URLField(max_length=255, blank=True)
    hash_archivo = models.CharField(max_length=64, blank=True, editable=False)
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ENTREGADA')
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_entrega']
        constraints = [
            models.UniqueConstraint(
                fields=['actividad', 'estudiante'],
                name='unique_entrega_por_actividad_estudiante'
            )
        ]

    def __str__(self):
        return f'{self.estudiante} - {self.actividad}'


class VersionEntrega(models.Model):
    entrega = models.ForeignKey(
        Entrega,
        on_delete=models.CASCADE,
        related_name='versiones'
    )
    archivo = models.FileField(upload_to='entregas/versiones/%Y/%m/%d/')
    repositorio_github = models.URLField(max_length=255, blank=True)
    hash_archivo = models.CharField(max_length=64, blank=True, editable=False)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=Entrega.ESTADO_CHOICES, default='REENTREGADA')

    class Meta:
        ordering = ['-fecha_subida']

    def __str__(self):
        return f'Versión de {self.entrega} ({self.fecha_subida:%d/%m/%Y})'


class EvidenciaValidacion(models.Model):
    CAPA_CHOICES = [
        ('ARCHIVO', 'Archivo'),
        ('INTEGRIDAD', 'Integridad'),
        ('METADATOS', 'Metadatos'),
        ('GITHUB', 'Repositorio GitHub'),
    ]

    entrega = models.ForeignKey(
        Entrega,
        on_delete=models.CASCADE,
        related_name='evidencias',
        null=True,
        blank=True,
    )
    version = models.ForeignKey(
        VersionEntrega,
        on_delete=models.CASCADE,
        related_name='evidencias',
        null=True,
        blank=True,
    )
    capa = models.CharField(max_length=20, choices=CAPA_CHOICES)
    aprobado = models.BooleanField()
    mensaje = models.TextField()
    comprobado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['capa', '-comprobado_en']

    def __str__(self):
        resultado = 'Aprobada' if self.aprobado else 'Rechazada'
        return f'{self.get_capa_display()}: {resultado}'
