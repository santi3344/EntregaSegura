from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

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


@override_settings(DOCENTE_REGISTRATION_CODE='CodigoDocente-2026')
class RegistroDocenteDirectoTests(TestCase):
	def datos_registro(self):
		return {
			'username': 'docente_nuevo',
			'first_name': 'Docente',
			'last_name': 'Nuevo',
			'email': 'docente.nuevo@example.com',
			'password1': 'F0r-Teacher!Secure-99',
			'password2': 'F0r-Teacher!Secure-99',
		}

	def test_registro_docente_crea_cuenta_y_perfil_inmediatamente(self):
		respuesta = self.client.post(
			reverse('registro_docente'),
			self.datos_registro(),
		)
		self.assertContains(respuesta, 'Tus datos fueron recibidos')
		respuesta = self.client.post(
			reverse('registro_docente'),
			{'codigo_docente': 'CodigoDocente-2026'},
			follow=True,
		)

		self.assertEqual(respuesta.status_code, 200)
		self.assertContains(respuesta, 'Cuenta docente creada correctamente')
		usuario = User.objects.get(username='docente_nuevo')
		self.assertTrue(usuario.check_password(self.datos_registro()['password1']))
		self.assertEqual(usuario.perfil.rol, 'DOCENTE')
		self.assertFalse(
			RegistroDocentePendiente.objects.filter(username='docente_nuevo').exists()
		)

	def test_registro_docente_acepta_email_vacio(self):
		datos = self.datos_registro()
		datos.pop('email')

		respuesta = self.client.post(reverse('registro_docente'), datos)
		self.assertContains(respuesta, 'Tus datos fueron recibidos')
		respuesta = self.client.post(
			reverse('registro_docente'),
			{'codigo_docente': 'CodigoDocente-2026'},
		)

		self.assertRedirects(respuesta, reverse('login'))
		self.assertEqual(User.objects.get(username='docente_nuevo').email, '')

	def test_codigo_invalido_no_crea_cuenta(self):
		datos = self.datos_registro()

		respuesta = self.client.post(reverse('registro_docente'), datos)
		self.assertContains(respuesta, 'Tus datos fueron recibidos')
		respuesta = self.client.post(
			reverse('registro_docente'),
			{'codigo_docente': 'codigo-incorrecto'},
		)

		self.assertEqual(respuesta.status_code, 200)
		self.assertContains(respuesta, 'El código institucional docente no es válido.')
		self.assertFalse(User.objects.filter(username='docente_nuevo').exists())
		self.assertFalse(Perfil.objects.filter(rol='DOCENTE').exists())

	@override_settings(DOCENTE_REGISTRATION_CODE='')
	def test_codigo_ausente_en_configuracion_bloquea_registro(self):
		respuesta = self.client.post(
			reverse('registro_docente'),
			self.datos_registro(),
		)
		self.assertContains(respuesta, 'Tus datos fueron recibidos')
		respuesta = self.client.post(
			reverse('registro_docente'),
			{'codigo_docente': 'CodigoDocente-2026'},
		)

		self.assertEqual(respuesta.status_code, 200)
		self.assertContains(respuesta, 'El código institucional docente no es válido.')
		self.assertFalse(User.objects.filter(username='docente_nuevo').exists())

	def test_registro_siempre_asigna_rol_docente_y_no_altera_estudiante(self):
		estudiante = User.objects.create_user(
			username='estudiante_existente',
			password='Clave-segura-123',
		)
		Perfil.objects.create(usuario=estudiante, rol='ESTUDIANTE')

		respuesta = self.client.post(reverse('registro_docente'), self.datos_registro())
		self.assertContains(respuesta, 'Tus datos fueron recibidos')
		respuesta = self.client.post(
			reverse('registro_docente'),
			{'codigo_docente': 'CodigoDocente-2026'},
		)

		self.assertRedirects(respuesta, reverse('login'))
		self.assertEqual(
			User.objects.get(username='estudiante_existente').perfil.rol,
			'ESTUDIANTE',
		)
		self.assertEqual(User.objects.get(username='docente_nuevo').perfil.rol, 'DOCENTE')


@override_settings(DOCENTE_REGISTRATION_CODE='')
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
		self.assertContains(registro, 'Tus datos fueron recibidos')
		registro = client.post(
			reverse('registro_docente'),
			{'codigo_docente': codigo},
		)

		self.assertRedirects(registro, reverse('login'))
		self.assertEqual(User.objects.get(username='docente_generado').perfil.rol, 'DOCENTE')
