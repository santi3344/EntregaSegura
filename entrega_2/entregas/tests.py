from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from unittest.mock import patch

from cursos.models import Curso, Grupo
from entregas.models import Actividad, Entrega, VersionEntrega
from entregas.validators import validate_submission
from usuarios.models import Perfil


class EntregasTests(TestCase):
    def setUp(self):
        self.docente_user = User.objects.create_user(username='docente1', password='123456')
        self.estudiante_user = User.objects.create_user(username='estudiante1', password='123456')

        Perfil.objects.create(usuario=self.docente_user, rol='DOCENTE')
        perfil_estudiante = Perfil.objects.create(usuario=self.estudiante_user, rol='ESTUDIANTE')

        self.curso = Curso.objects.create(nombre='Matemáticas', descripcion='Curso de prueba', docente=self.docente_user)
        self.grupo = Grupo.objects.create(nombre='A', curso=self.curso)
        self.grupo.estudiantes.add(perfil_estudiante)

        self.actividad = Actividad.objects.create(
            titulo='Tarea 1',
            descripcion='Resolver ejercicios',
            curso=self.curso,
            fecha_limite='2026-10-15T20:00:00Z',
            creado_por=self.docente_user,
        )

    def test_crear_entrega_y_version(self):
        perfil = Perfil.objects.get(usuario=self.estudiante_user)
        archivo = SimpleUploadedFile('entrega.pdf', b'contenido', content_type='application/pdf')

        entrega = Entrega.objects.create(
            actividad=self.actividad,
            estudiante=perfil,
            archivo=archivo,
            estado='ENTREGADA',
        )

        version = VersionEntrega.objects.create(
            entrega=entrega,
            archivo=SimpleUploadedFile('version2.pdf', b'contenido 2', content_type='application/pdf'),
            comentario='Reentrega',
            estado='REENTREGADA',
        )

        self.assertEqual(entrega.estudiante.usuario.username, 'estudiante1')
        self.assertEqual(version.entrega, entrega)
        self.assertEqual(entrega.versiones.count(), 1)

    def test_actividad_queda_asociada_al_grupo_y_curso(self):
        self.assertEqual(self.actividad.curso, self.curso)
        self.assertIn(self.actividad, self.curso.actividades.all())

    def test_docente_puede_ver_actividades_creadas_en_lista(self):
        client = Client(HTTP_HOST='127.0.0.1:8000')
        client.force_login(self.docente_user)

        response = client.get(reverse('entregas_docente:lista_entregas_docente'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tarea 1')

    @patch('entregas.validators.github_repository_status')
    def test_las_cuatro_capas_de_validacion_aprueban_una_entrega_valida(self, github_status):
        github_status.return_value = (True, 'Repositorio verificado.')
        perfil = Perfil.objects.get(usuario=self.estudiante_user)
        archivo = SimpleUploadedFile(
            'entrega.pdf', b'contenido valido', content_type='application/pdf'
        )

        resultados = validate_submission(
            archivo,
            'https://github.com/santi3344/EntregaSegura',
            self.actividad,
            perfil,
        )

        self.assertEqual(
            {capa for capa in resultados if capa != 'hash_archivo'},
            {'ARCHIVO', 'INTEGRIDAD', 'METADATOS', 'GITHUB'},
        )
        self.assertTrue(all(resultados[capa][0] for capa in (
            'ARCHIVO', 'INTEGRIDAD', 'METADATOS', 'GITHUB'
        )))
        self.assertEqual(len(resultados['hash_archivo']), 64)
