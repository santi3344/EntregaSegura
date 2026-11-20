import re
from datetime import timedelta

from django.core import mail
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone

from .models import CodigoRegistroDocente, Perfil, RegistroDocentePendiente


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


@override_settings(
	EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
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

	def test_registro_docente_solo_crea_cuenta_tras_verificar_correo(self):
		respuesta, pendiente, codigo = self.iniciar_registro()

		self.assertRedirects(
			respuesta,
			reverse('verificar_registro_docente', args=[pendiente.pk]),
		)
		self.assertEqual(mail.outbox[-1].to, ['docente.nuevo@example.com'])
		self.assertFalse(User.objects.filter(username='docente_nuevo').exists())
		self.assertNotEqual(pendiente.codigo_hash, codigo)
		self.assertNotEqual(
			pendiente.password_hash,
			self.datos_registro()['password1'],
		)

		respuesta = self.client.post(
			reverse('verificar_registro_docente', args=[pendiente.pk]),
			{'codigo': codigo},
		)

		self.assertRedirects(respuesta, reverse('login'))
		usuario = User.objects.get(username='docente_nuevo')
		self.assertTrue(usuario.check_password(self.datos_registro()['password1']))
		self.assertEqual(usuario.perfil.rol, 'DOCENTE')
		self.assertFalse(
			RegistroDocentePendiente.objects.filter(username='docente_nuevo').exists()
		)

	def test_registro_docente_requiere_correo(self):
		datos = self.datos_registro()
		datos.pop('email')

		respuesta = self.client.post(reverse('registro_docente'), datos)
		self.assertEqual(respuesta.status_code, 200)
		self.assertContains(respuesta, 'This field is required.')
		self.assertFalse(User.objects.filter(username='docente_nuevo').exists())

	def test_codigo_invalido_no_crea_cuenta(self):
		_, pendiente, _ = self.iniciar_registro()
		respuesta = self.client.post(
			reverse('verificar_registro_docente', args=[pendiente.pk]),
			{'codigo': '000000'},
		)

		self.assertEqual(respuesta.status_code, 200)
		self.assertContains(respuesta, 'El código no es correcto.')
		self.assertFalse(User.objects.filter(username='docente_nuevo').exists())

	def test_codigo_vencido_no_crea_cuenta(self):
		_, pendiente, _ = self.iniciar_registro()
		pendiente.expira_en = timezone.now() - timedelta(seconds=1)
		pendiente.save(update_fields=['expira_en'])

		respuesta = self.client.get(
			reverse('verificar_registro_docente', args=[pendiente.pk]),
		)

		self.assertContains(respuesta, 'El código venció')
		self.assertFalse(User.objects.filter(username='docente_nuevo').exists())

	def test_quinto_codigo_incorrecto_bloquea_verificacion(self):
		_, pendiente, _ = self.iniciar_registro()
		url = reverse('verificar_registro_docente', args=[pendiente.pk])
		for _ in range(5):
			respuesta = self.client.post(url, {'codigo': '000000'})

		self.assertContains(respuesta, 'Verificación bloqueada')
		self.assertFalse(User.objects.filter(username='docente_nuevo').exists())

	def test_no_envia_dos_codigos_mientras_hay_verificacion_vigente(self):
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


@override_settings(
	DOCENTE_REGISTRATION_CODE='',
	EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
class CodigoRegistroDocenteTests(TestCase):
	def test_acceso_no_autorizado_redirige_al_login(self):
		respuesta = self.client.get(reverse('gestionar_codigo_registro_docente'))

		self.assertRedirects(
			respuesta,
			f"{reverse('login')}?next={reverse('gestionar_codigo_registro_docente')}",
		)

	def test_usuario_autenticado_no_staff_recibe_prohibido(self):
		usuario = User.objects.create_user(username='estudiante', password='Clave-segura-123')
		self.client.force_login(usuario)

		self.assertEqual(
			self.client.get(reverse('gestionar_codigo_registro_docente')).status_code,
			403,
		)

	def test_staff_genera_codigo_y_solo_se_muestra_en_la_respuesta(self):
		administrador = User.objects.create_user(
			username='admin_codigo',
			password='Clave-segura-123',
			is_staff=True,
		)
		self.client.force_login(administrador)

		respuesta = self.client.post(reverse('gestionar_codigo_registro_docente'))

		self.assertEqual(respuesta.status_code, 200)
		codigo = respuesta.context['codigo_generado']
		self.assertTrue(codigo)
		self.assertContains(respuesta, codigo)
		configuracion = CodigoRegistroDocente.objects.get(clave='docente')
		self.assertTrue(check_password(codigo, configuracion.codigo_hash))
		self.assertNotContains(
			self.client.get(reverse('gestionar_codigo_registro_docente')),
			codigo,
		)

	def test_registro_directo_acepta_codigo_generado(self):
		administrador = User.objects.create_user(
			username='admin_codigo',
			password='Clave-segura-123',
			is_superuser=True,
			is_staff=True,
		)
		self.client.force_login(administrador)
		respuesta_generacion = self.client.post(
			reverse('gestionar_codigo_registro_docente')
		)
		codigo = respuesta_generacion.context['codigo_generado']

		client = Client()
		registro = client.post(
			reverse('registro_docente'),
			{
				'username': 'docente_generado',
				'first_name': 'Docente',
				'last_name': 'Generado',
				'email': 'generado@example.com',
				'password1': 'F0r-Teacher!Secure-99',
				'password2': 'F0r-Teacher!Secure-99',
			},
		)
		self.assertRedirects(
			registro,
			reverse(
				'verificar_registro_docente',
				args=[RegistroDocentePendiente.objects.get(
					username='docente_generado',
				).pk],
			),
		)
		self.assertEqual(len(mail.outbox), 1)
