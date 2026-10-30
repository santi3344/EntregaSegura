from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from cursos.models import Curso, Grupo
from usuarios.models import Perfil


class DocenteCursosGruposTests(TestCase):
	def setUp(self):
		self.docente = User.objects.create_user(
			username='docente_crud',
			password='Clave-segura-123',
		)
		Perfil.objects.create(usuario=self.docente, rol='DOCENTE')
		self.otro_docente = User.objects.create_user(
			username='otro_docente',
			password='Clave-segura-123',
		)
		Perfil.objects.create(usuario=self.otro_docente, rol='DOCENTE')
		self.estudiante = User.objects.create_user(
			username='estudiante_crud',
			password='Clave-segura-123',
		)
		Perfil.objects.create(usuario=self.estudiante, rol='ESTUDIANTE')

		self.curso = Curso.objects.create(
			nombre='Álgebra',
			descripcion='Curso inicial',
			docente=self.docente,
		)
		self.curso_ajeno = Curso.objects.create(
			nombre='Historia',
			docente=self.otro_docente,
		)
		self.grupo = Grupo.objects.create(nombre='A', curso=self.curso)
		self.grupo_ajeno = Grupo.objects.create(
			nombre='B',
			curso=self.curso_ajeno,
		)
		self.client.force_login(self.docente)

	def test_docente_crea_y_edita_curso_sin_poder_asignar_otro_dueno(self):
		respuesta = self.client.post(
			reverse('cursos:lista_cursos'),
			{
				'nombre': 'Geometría',
				'descripcion': 'Segundo curso',
				'docente': self.otro_docente.pk,
			},
		)

		creado = Curso.objects.get(nombre='Geometría')
		self.assertRedirects(respuesta, reverse('cursos:lista_cursos'))
		self.assertEqual(creado.docente, self.docente)

		respuesta = self.client.post(
			reverse('cursos:editar_curso', args=[creado.pk]),
			{'nombre': 'Geometría avanzada', 'descripcion': 'Actualizado'},
		)
		creado.refresh_from_db()
		self.assertRedirects(respuesta, reverse('cursos:lista_cursos'))
		self.assertEqual(creado.nombre, 'Geometría avanzada')

	def test_docente_elimina_curso_y_sus_grupos(self):
		confirmar = self.client.get(
			reverse('cursos:eliminar_curso', args=[self.curso.pk])
		)
		self.assertEqual(confirmar.status_code, 200)

		respuesta = self.client.post(
			reverse('cursos:eliminar_curso', args=[self.curso.pk])
		)
		self.assertRedirects(respuesta, reverse('cursos:lista_cursos'))
		self.assertFalse(Curso.objects.filter(pk=self.curso.pk).exists())
		self.assertFalse(Grupo.objects.filter(pk=self.grupo.pk).exists())

	def test_docente_no_puede_ver_ni_modificar_curso_ajeno(self):
		editar = self.client.get(
			reverse('cursos:editar_curso', args=[self.curso_ajeno.pk])
		)
		eliminar = self.client.post(
			reverse('cursos:eliminar_curso', args=[self.curso_ajeno.pk])
		)

		self.assertEqual(editar.status_code, 404)
		self.assertEqual(eliminar.status_code, 404)
		self.assertTrue(Curso.objects.filter(pk=self.curso_ajeno.pk).exists())

	def test_docente_crea_edita_y_elimina_grupo_de_su_curso(self):
		respuesta = self.client.post(
			reverse('cursos:lista_grupos'),
			{
				'nombre': 'C',
				'curso': self.curso.pk,
				'estudiantes': [Perfil.objects.get(usuario=self.estudiante).pk],
			},
		)
		creado = Grupo.objects.get(nombre='C', curso=self.curso)
		self.assertRedirects(respuesta, reverse('cursos:lista_grupos'))
		self.assertTrue(
			creado.estudiantes.filter(usuario=self.estudiante).exists()
		)

		respuesta = self.client.post(
			reverse('cursos:editar_grupo', args=[creado.pk]),
			{'nombre': 'C actualizado', 'curso': self.curso.pk},
		)
		creado.refresh_from_db()
		self.assertRedirects(respuesta, reverse('cursos:lista_grupos'))
		self.assertEqual(creado.nombre, 'C actualizado')

		respuesta = self.client.post(
			reverse('cursos:eliminar_grupo', args=[creado.pk])
		)
		self.assertRedirects(respuesta, reverse('cursos:lista_grupos'))
		self.assertFalse(Grupo.objects.filter(pk=creado.pk).exists())

	def test_no_se_puede_asignar_grupo_a_curso_de_otro_docente(self):
		respuesta = self.client.post(
			reverse('cursos:lista_grupos'),
			{'nombre': 'No autorizado', 'curso': self.curso_ajeno.pk},
		)

		self.assertEqual(respuesta.status_code, 200)
		self.assertFalse(Grupo.objects.filter(nombre='No autorizado').exists())

	def test_docente_no_puede_modificar_grupo_ajeno(self):
		respuesta = self.client.get(
			reverse('cursos:editar_grupo', args=[self.grupo_ajeno.pk])
		)

		self.assertEqual(respuesta.status_code, 404)
		self.assertTrue(Grupo.objects.filter(pk=self.grupo_ajeno.pk).exists())

	def test_estudiante_no_puede_entrar_a_gestion_docente(self):
		self.client.force_login(self.estudiante)

		respuesta = self.client.get(reverse('cursos:lista_cursos'))

		self.assertRedirects(respuesta, reverse('inicio'))

	def test_panel_muestra_conteo_de_cursos_y_grupos(self):
		respuesta = self.client.get(reverse('panel_docente'))

		self.assertEqual(respuesta.context['total_cursos'], 1)
		self.assertEqual(respuesta.context['total_grupos'], 1)
		self.assertContains(respuesta, reverse('cursos:lista_cursos'))
		self.assertContains(respuesta, reverse('cursos:lista_grupos'))


class AsignacionYVisibilidadEstudianteTests(TestCase):
	def setUp(self):
		self.docente = User.objects.create_user(
			username='docente_asignacion',
			password='Clave-segura-123',
		)
		Perfil.objects.create(usuario=self.docente, rol='DOCENTE')
		self.estudiante = User.objects.create_user(
			username='estudiante_asignado',
			first_name='Ana',
			password='Clave-segura-123',
		)
		self.perfil_estudiante = Perfil.objects.create(
			usuario=self.estudiante,
			rol='ESTUDIANTE',
		)
		self.otro_estudiante = User.objects.create_user(
			username='estudiante_no_asignado',
			password='Clave-segura-123',
		)
		self.perfil_otro_estudiante = Perfil.objects.create(
			usuario=self.otro_estudiante,
			rol='ESTUDIANTE',
		)
		self.curso_asignado = Curso.objects.create(
			nombre='Ciencias',
			docente=self.docente,
		)
		self.grupo_asignado = Grupo.objects.create(
			nombre='Grupo 1',
			curso=self.curso_asignado,
		)
		self.otro_curso = Curso.objects.create(
			nombre='Literatura',
			docente=self.docente,
		)
		self.otro_grupo = Grupo.objects.create(
			nombre='Grupo 2',
			curso=self.otro_curso,
		)
		self.grupo_asignado.estudiantes.add(self.perfil_estudiante)

	def test_docente_asigna_estudiante_y_formulario_rechaza_docente(self):
		self.client.force_login(self.docente)
		respuesta = self.client.post(
			reverse('cursos:editar_grupo', args=[self.otro_grupo.pk]),
			{
				'nombre': 'Grupo 2',
				'curso': self.otro_curso.pk,
				'estudiantes': [self.perfil_estudiante.pk],
			},
		)
		self.assertRedirects(respuesta, reverse('cursos:lista_grupos'))
		self.assertTrue(
			self.otro_grupo.estudiantes.filter(pk=self.perfil_estudiante.pk).exists()
		)

		respuesta = self.client.post(
			reverse('cursos:editar_grupo', args=[self.otro_grupo.pk]),
			{
				'nombre': 'Grupo 2',
				'curso': self.otro_curso.pk,
				'estudiantes': [Perfil.objects.get(usuario=self.docente).pk],
			},
		)
		self.assertEqual(respuesta.status_code, 200)
		self.assertTrue(
			self.otro_grupo.estudiantes.filter(pk=self.perfil_estudiante.pk).exists()
		)

	def test_estudiante_ve_solo_grupos_asignados_y_cursos_sin_duplicados(self):
		segundo_grupo_mismo_curso = Grupo.objects.create(
			nombre='Grupo 1B',
			curso=self.curso_asignado,
		)
		segundo_grupo_mismo_curso.estudiantes.add(self.perfil_estudiante)
		self.otro_grupo.estudiantes.add(self.perfil_otro_estudiante)
		self.client.force_login(self.estudiante)

		panel = self.client.get(reverse('panel_estudiante'))
		cursos = self.client.get(reverse('mis_cursos'))
		grupos = self.client.get(reverse('mis_grupos'))

		self.assertEqual(panel.status_code, 200)
		self.assertEqual(len(panel.context['cursos']), 1)
		self.assertEqual(len(panel.context['grupos']), 2)
		self.assertContains(cursos, 'Ciencias')
		self.assertNotContains(cursos, 'Literatura')
		self.assertContains(grupos, 'Grupo 1')
		self.assertContains(grupos, 'Grupo 1B')
		self.assertNotContains(grupos, 'Grupo 2')

	def test_estudiante_no_accede_a_listas_docentes(self):
		self.client.force_login(self.estudiante)

		respuesta = self.client.get(reverse('cursos:lista_grupos'))

		self.assertRedirects(respuesta, reverse('inicio'))

	def test_docente_no_accede_a_listas_de_estudiante(self):
		self.client.force_login(self.docente)

		respuesta = self.client.get(reverse('mis_cursos'))

		self.assertRedirects(respuesta, reverse('inicio'))

# Create your tests here.
