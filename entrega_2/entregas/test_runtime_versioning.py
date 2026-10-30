from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cursos.models import Curso, Grupo
from entregas.models import Actividad, Entrega, EvidenciaValidacion, VersionEntrega
from usuarios.models import Perfil


class RuntimeVersioningTests(TestCase):
    def test_version_and_validation_evidence_are_read_back_from_detail(self):
        docente = User.objects.create_user(username='version_docente')
        estudiante = User.objects.create_user(
            username='version_estudiante',
            password='VersionPass!2026',
        )
        perfil = Perfil.objects.create(usuario=estudiante, rol='ESTUDIANTE')
        curso = Curso.objects.create(nombre='Versiones', docente=docente)
        grupo = Grupo.objects.create(nombre='A', curso=curso)
        grupo.estudiantes.add(perfil)
        actividad = Actividad.objects.create(
            titulo='Versiones',
            curso=curso,
            fecha_limite=timezone.now() + timedelta(days=1),
            creado_por=docente,
        )
        entrega = Entrega.objects.create(
            actividad=actividad,
            estudiante=perfil,
            archivo=SimpleUploadedFile('original.pdf', b'original'),
        )
        version = VersionEntrega.objects.create(
            entrega=entrega,
            archivo=SimpleUploadedFile('version2.pdf', b'version 2'),
            repositorio_github='https://github.com/santi3344/EntregaSegura',
        )
        EvidenciaValidacion.objects.create(
            version=version,
            capa='INTEGRIDAD',
            aprobado=True,
            mensaje='Hash comprobado.',
        )

        self.client.force_login(estudiante)
        response = self.client.get(
            reverse('entregas_estudiante:detalle_entrega', args=[entrega.pk])
        )
        self.assertContains(response, 'Versiones registradas')
        self.assertContains(response, 'Hash comprobado.')
from datetime import timedelta
