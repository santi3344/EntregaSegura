from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from usuarios.models import Perfil

from .forms import CursoForm, GrupoForm
from .models import Curso, Grupo


def docente_required(view_func):
	@wraps(view_func)
	@login_required
	def _wrapped_view(request, *args, **kwargs):
		es_docente = Perfil.objects.filter(
			usuario=request.user,
			rol='DOCENTE',
		).exists()
		if not es_docente:
			return redirect('inicio')
		return view_func(request, *args, **kwargs)

	return _wrapped_view


@docente_required
def lista_cursos(request):
	curso_edicion = None
	form = CursoForm(request.POST if request.method == 'POST' else None)

	if request.method == 'POST' and form.is_valid():
		curso = form.save(commit=False)
		curso.docente = request.user
		curso.save()
		messages.success(request, 'El curso se creó correctamente.')
		return redirect('cursos:lista_cursos')

	cursos = Curso.objects.filter(docente=request.user).annotate(
		total_grupos=Count('grupos')
	).order_by('nombre')
	return render(request, 'cursos/lista_cursos.html', {
		'form': form,
		'cursos': cursos,
		'curso_edicion': curso_edicion,
	})


@docente_required
def editar_curso(request, pk):
	curso = get_object_or_404(Curso, pk=pk, docente=request.user)
	form = CursoForm(request.POST or None, instance=curso)

	if request.method == 'POST' and form.is_valid():
		form.save()
		messages.success(request, 'El curso se actualizó correctamente.')
		return redirect('cursos:lista_cursos')

	cursos = Curso.objects.filter(docente=request.user).annotate(
		total_grupos=Count('grupos')
	).order_by('nombre')
	return render(request, 'cursos/lista_cursos.html', {
		'form': form,
		'cursos': cursos,
		'curso_edicion': curso,
	})


@docente_required
def eliminar_curso(request, pk):
	curso = get_object_or_404(Curso, pk=pk, docente=request.user)
	if request.method == 'POST':
		curso.delete()
		messages.success(request, 'El curso y sus grupos se eliminaron correctamente.')
		return redirect('cursos:lista_cursos')

	return render(request, 'cursos/confirmar_eliminacion.html', {
		'objeto': curso,
		'tipo': 'curso',
		'cancel_url': reverse('cursos:lista_cursos'),
	})


@docente_required
def lista_grupos(request):
	grupo_edicion = None
	initial = {}
	curso_id = request.GET.get('curso')
	if curso_id:
		curso = get_object_or_404(Curso, pk=curso_id, docente=request.user)
		initial['curso'] = curso

	form = GrupoForm(
		request.POST if request.method == 'POST' else None,
		user=request.user,
		initial=initial,
	)
	if request.method == 'POST' and form.is_valid():
		form.save()
		messages.success(request, 'El grupo se creó correctamente.')
		return redirect('cursos:lista_grupos')

	grupos = Grupo.objects.filter(curso__docente=request.user).select_related(
		'curso'
	).order_by('curso__nombre', 'nombre')
	return render(request, 'cursos/lista_grupos.html', {
		'form': form,
		'grupos': grupos,
		'grupo_edicion': grupo_edicion,
	})


@docente_required
def editar_grupo(request, pk):
	grupo = get_object_or_404(Grupo, pk=pk, curso__docente=request.user)
	form = GrupoForm(
		request.POST if request.method == 'POST' else None,
		user=request.user,
		instance=grupo,
	)

	if request.method == 'POST' and form.is_valid():
		form.save()
		messages.success(request, 'El grupo se actualizó correctamente.')
		return redirect('cursos:lista_grupos')

	grupos = Grupo.objects.filter(curso__docente=request.user).select_related(
		'curso'
	).order_by('curso__nombre', 'nombre')
	return render(request, 'cursos/lista_grupos.html', {
		'form': form,
		'grupos': grupos,
		'grupo_edicion': grupo,
	})


@docente_required
def eliminar_grupo(request, pk):
	grupo = get_object_or_404(Grupo, pk=pk, curso__docente=request.user)
	if request.method == 'POST':
		grupo.delete()
		messages.success(request, 'El grupo se eliminó correctamente.')
		return redirect('cursos:lista_grupos')

	return render(request, 'cursos/confirmar_eliminacion.html', {
		'objeto': grupo,
		'tipo': 'grupo',
		'cancel_url': reverse('cursos:lista_grupos'),
	})
