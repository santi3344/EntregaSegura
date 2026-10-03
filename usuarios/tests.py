from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Perfil


class AccesoPanelesTests(TestCase):
	def setUp(self):
		self.docente = User.objects.create_user(
			username='docente',
			password='Clave-segura-123',
		)
		Perfil.objects.create(usuario=self.docente, rol='DOCENTE')

		self.estudiante = User.objects.create_user(
			username='estudiante',
			password='Clave-segura-123',
		)
		Perfil.objects.create(usuario=self.estudiante, rol='ESTUDIANTE')

	def test_login_docente_con_csrf_redirige_al_panel(self):
		client = Client(enforce_csrf_checks=True)
		pagina_login = client.get(reverse('login'))

		self.assertEqual(pagina_login.status_code, 200)
		self.assertIn('csrftoken', client.cookies)

		respuesta = client.post(
			reverse('login'),
			{
				'usuario': 'docente',
				'password': 'Clave-segura-123',
				'csrfmiddlewaretoken': client.cookies['csrftoken'].value,
			},
		)

		self.assertRedirects(respuesta, reverse('panel_docente'))
		panel = client.get(reverse('panel_docente'))
		self.assertEqual(panel.status_code, 200)
		self.assertContains(panel, 'Panel docente')

	def test_login_estudiante_redirige_al_panel(self):
		respuesta = self.client.post(
			reverse('login'),
			{'usuario': 'estudiante', 'password': 'Clave-segura-123'},
		)

		self.assertRedirects(respuesta, reverse('panel_estudiante'))
		panel = self.client.get(reverse('panel_estudiante'))
		self.assertEqual(panel.status_code, 200)
		self.assertContains(panel, 'Panel estudiante')

	def test_panel_protegido_redirige_al_login(self):
		respuesta = self.client.get(reverse('panel_docente'))

		self.assertRedirects(
			respuesta,
			f"{reverse('login')}?next={reverse('panel_docente')}",
		)

	def test_login_sin_csrf_token_es_rechazado(self):
		client = Client(enforce_csrf_checks=True)

		respuesta = client.post(
			reverse('login'),
			{'usuario': 'docente', 'password': 'Clave-segura-123'},
		)

		self.assertEqual(respuesta.status_code, 403)
