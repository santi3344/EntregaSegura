import re
from datetime import timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Perfil, RegistroDocentePendiente


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

	def test_perfil_muestra_cerrar_sesion_y_permite_cambiar_de_rol(self):
		for usuario, nombre_panel in (
			(self.docente, 'panel_docente'),
			(self.estudiante, 'panel_estudiante'),
		):
			with self.subTest(rol=usuario.perfil.rol):
				self.client.force_login(usuario)
				panel = self.client.get(reverse(nombre_panel))

				self.assertContains(panel, 'Cerrar sesión')
				self.assertContains(panel, reverse('logout'))

				respuesta = self.client.get(reverse('logout'))
				self.assertRedirects(respuesta, reverse('login'))
				self.assertNotIn('_auth_user_id', self.client.session)

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


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class RegistroDocenteVerificadoTests(TestCase):
	def datos_registro(self):
		return {
			'username': 'docente_nuevo',
			'first_name': 'Docente',
			'last_name': 'Nuevo',
			'email': 'docente.nuevo@example.com',
			'password1': 'F0r-Teacher!Secure-99',
			'password2': 'F0r-Teacher!Secure-99',
		}

	def iniciar_registro(self):
		respuesta = self.client.post(
			reverse('registro_docente'),
			self.datos_registro(),
		)
		pendiente = RegistroDocentePendiente.objects.get(
			username='docente_nuevo',
		)
		codigo = re.search(r'\b(\d{6})\b', mail.outbox[-1].body).group(1)
		return respuesta, pendiente, codigo

	def test_registro_docente_solo_se_crea_tras_verificar_codigo(self):
		respuesta, pendiente, codigo = self.iniciar_registro()

		self.assertRedirects(
			respuesta,
		reverse('verificar_registro_docente', args=[pendiente.pk]),
		)
		self.assertFalse(User.objects.filter(username='docente_nuevo').exists())
		self.assertEqual(mail.outbox[-1].to, ['docente.nuevo@example.com'])
		self.assertNotEqual(pendiente.codigo_hash, codigo)
		self.assertNotEqual(pendiente.password_hash, self.datos_registro()['password1'])

		respuesta = self.client.post(
			reverse('verificar_registro_docente', args=[pendiente.pk]),
			{'codigo': codigo},
		)

		self.assertRedirects(respuesta, reverse('login'))
		usuario = User.objects.get(username='docente_nuevo')
		self.assertTrue(usuario.check_password(self.datos_registro()['password1']))
		self.assertEqual(usuario.perfil.rol, 'DOCENTE')
		self.assertFalse(RegistroDocentePendiente.objects.filter(pk=pendiente.pk).exists())

	def test_codigo_incorrecto_bloquea_al_quinto_intento(self):
		_, pendiente, _ = self.iniciar_registro()
		url = reverse('verificar_registro_docente', args=[pendiente.pk])

		for _ in range(5):
			respuesta = self.client.post(url, {'codigo': '000000'})

		self.assertContains(respuesta, 'Verificación bloqueada')
		self.assertFalse(User.objects.filter(username='docente_nuevo').exists())
		self.assertFalse(RegistroDocentePendiente.objects.filter(pk=pendiente.pk).exists())

	def test_codigo_vencido_no_crea_la_cuenta(self):
		_, pendiente, _ = self.iniciar_registro()
		pendiente.expira_en = timezone.now() - timedelta(seconds=1)
		pendiente.save(update_fields=['expira_en'])

		respuesta = self.client.get(
			reverse('verificar_registro_docente', args=[pendiente.pk]),
		)

		self.assertContains(respuesta, 'El código venció')
		self.assertFalse(User.objects.filter(username='docente_nuevo').exists())
		self.assertFalse(RegistroDocentePendiente.objects.filter(pk=pendiente.pk).exists())

	def test_no_envia_varios_codigos_al_mismo_correo_mientras_hay_uno_vigente(self):
		self.iniciar_registro()
		respuesta = self.client.post(
			reverse('registro_docente'),
			{
				**self.datos_registro(),
				'username': 'docente_otro',
			},
		)

		self.assertContains(respuesta, 'verificación pendiente')
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(RegistroDocentePendiente.objects.count(), 1)

	def test_login_muestra_enlace_para_crear_cuenta_docente(self):
		respuesta = self.client.get(reverse('login'))
		self.assertContains(respuesta, reverse('registro_docente'))
