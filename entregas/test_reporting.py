from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cursos.models import Curso, Grupo
from usuarios.models import Perfil

from .models import Actividad, Entrega, EvidenciaValidacion


class ReportingTests(TestCase):
    def setUp(self):
        self.docente = User.objects.create_user(username='report_docente')
        self.student = User.objects.create_user(username='report_student')
        Perfil.objects.create(usuario=self.docente, rol='DOCENTE')
        profile = Perfil.objects.create(usuario=self.student, rol='ESTUDIANTE')
        course = Curso.objects.create(nombre='Reporte', docente=self.docente)
        group = Grupo.objects.create(nombre='A', curso=course)
        group.estudiantes.add(profile)
        activity = Actividad.objects.create(
            titulo='Actividad reporte',
            curso=course,
            fecha_limite=timezone.now() + timedelta(days=1),
            creado_por=self.docente,
        )
        self.delivery = Entrega.objects.create(
            actividad=activity,
            estudiante=profile,
            archivo=SimpleUploadedFile('report.pdf', b'report'),
            repositorio_github='https://github.com/santi3344/EntregaSegura',
        )
        EvidenciaValidacion.objects.create(
            entrega=self.delivery,
            capa='ARCHIVO',
            aprobado=True,
            mensaje='Correcto',
        )
        self.client.force_login(self.docente)

    def test_filter_page_and_csv_export_are_scoped_to_teacher(self):
        page = self.client.get(reverse('entregas_docente:lista_entregas_docente'), {
            'estado': 'ENTREGADA',
        })
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Actividad reporte')

        csv_response = self.client.get(
            reverse('entregas_docente:lista_entregas_docente'),
            {'export': 'csv', 'estudiante': 'report_student'},
        )
        self.assertEqual(csv_response.status_code, 200)
        self.assertEqual(csv_response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('report_student', csv_response.content.decode('utf-8-sig'))
