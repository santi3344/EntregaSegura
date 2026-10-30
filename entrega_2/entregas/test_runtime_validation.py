from unittest.mock import patch
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from cursos.models import Curso, Grupo
from entregas.models import Actividad
from usuarios.models import Perfil

from .validators import validate_submission


class RuntimeValidationTests(TestCase):
    def setUp(self):
        self.docente = User.objects.create_user(username='runtime_docente')
        self.estudiante = User.objects.create_user(username='runtime_estudiante')
        self.perfil = Perfil.objects.create(
            usuario=self.estudiante, rol='ESTUDIANTE'
        )
        Perfil.objects.create(usuario=self.docente, rol='DOCENTE')
        curso = Curso.objects.create(
            nombre='Runtime',
            descripcion='Pruebas',
            docente=self.docente,
        )
        grupo = Grupo.objects.create(nombre='A', curso=curso)
        grupo.estudiantes.add(self.perfil)
        self.actividad = Actividad.objects.create(
            titulo='Runtime',
            curso=curso,
            fecha_limite=timezone.now() + timedelta(days=1),
            creado_por=self.docente,
        )

    @patch('entregas.validators.github_repository_status')
    def test_four_layers_validate_a_real_uploaded_file(self, github_status):
        github_status.return_value = (True, 'Repositorio verificado.')
        result = validate_submission(
            SimpleUploadedFile('runtime.pdf', b'contenido'),
            'https://github.com/santi3344/EntregaSegura',
            self.actividad,
            self.perfil,
        )
        self.assertTrue(all(result[layer][0] for layer in (
            'ARCHIVO', 'INTEGRIDAD', 'METADATOS', 'GITHUB'
        )))
        self.assertEqual(len(result['hash_archivo']), 64)
