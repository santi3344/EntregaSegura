from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.models import Perfil

from .forms import ActividadForm, EntregaForm, VersionEntregaForm
from .models import Actividad, Entrega, VersionEntrega
from .reporting import export_entregas_csv


def _entregas_docente_context(request):
    actividades = Actividad.objects.filter(
        curso__docente=request.user
    ).select_related('curso', 'creado_por').order_by('-creado_en')
    entregas = Entrega.objects.filter(
        actividad__curso__docente=request.user
    ).select_related('actividad__curso', 'estudiante__usuario').prefetch_related(
        'evidencias', 'versiones'
    ).order_by('-fecha_entrega')
    filtros = {
        'curso': request.GET.get('curso', ''),
        'actividad': request.GET.get('actividad', ''),
        'estado': request.GET.get('estado', ''),
        'estudiante': request.GET.get('estudiante', '').strip(),
        'desde': request.GET.get('desde', ''),
        'hasta': request.GET.get('hasta', ''),
    }
    if filtros['curso'].isdigit():
        entregas = entregas.filter(actividad__curso_id=int(filtros['curso']))
    if filtros['actividad'].isdigit():
        entregas = entregas.filter(actividad_id=int(filtros['actividad']))
    if filtros['estado'] in dict(Entrega.ESTADO_CHOICES):
        entregas = entregas.filter(estado=filtros['estado'])
    if filtros['estudiante']:
        entregas = entregas.filter(
            estudiante__usuario__username__icontains=filtros['estudiante']
        )
    for field, lookup in (('desde', 'gte'), ('hasta', 'lte')):
        if filtros[field]:
            try:
                date_value = datetime.strptime(filtros[field], '%Y-%m-%d').date()
            except ValueError:
                filtros[field] = ''
            else:
                entregas = entregas.filter(**{f'fecha_entrega__date__{lookup}': date_value})
    return {
        'actividades': actividades,
        'entregas': entregas,
        'cursos_filtro': actividades.values_list('curso_id', 'curso__nombre').distinct(),
        'filtros': filtros,
        'estados': Entrega.ESTADO_CHOICES,
    }
from .validators import (
    raise_for_failed_validations,
    save_validation_evidence,
    validate_submission,
)


def estudiante_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        perfil = Perfil.objects.filter(usuario=request.user, rol='ESTUDIANTE').first()
        if perfil is None:
            return redirect('inicio')
        return view_func(request, *args, **kwargs)
    return _wrapped


def docente_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        perfil = Perfil.objects.filter(usuario=request.user, rol='DOCENTE').first()
        if perfil is None:
            return redirect('inicio')
        return view_func(request, *args, **kwargs)
    return _wrapped


@login_required
@estudiante_required
def mis_entregas(request):
    perfil = Perfil.objects.get(usuario=request.user, rol='ESTUDIANTE')
    entregas = Entrega.objects.filter(estudiante=perfil).select_related('actividad__curso').prefetch_related('versiones').order_by('-fecha_entrega')
    return render(request, 'entregas/lista_mis_entregas.html', {'entregas': entregas})


@login_required
@estudiante_required
def crear_entrega(request):
    perfil = Perfil.objects.get(usuario=request.user, rol='ESTUDIANTE')
    if request.method == 'POST':
        form = EntregaForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            entrega = form.save(commit=False)
            entrega.estudiante = perfil
            entrega.estado = 'ENTREGADA'
            resultados = validate_submission(
                form.cleaned_data['archivo'],
                form.cleaned_data['repositorio_github'],
                entrega.actividad,
                perfil,
            )
            try:
                raise_for_failed_validations(resultados)
            except ValidationError as error:
                form.add_error(None, error)
            else:
                entrega.hash_archivo = resultados['hash_archivo']
                entrega.save()
                save_validation_evidence(resultados, entrega=entrega)
                return redirect('entregas_estudiante:detalle_entrega', pk=entrega.pk)
    else:
        form = EntregaForm(request.user)
    return render(request, 'entregas/crear_entrega.html', {'form': form})


@login_required
@estudiante_required
def detalle_entrega(request, pk):
    perfil = Perfil.objects.get(usuario=request.user, rol='ESTUDIANTE')
    entrega = get_object_or_404(Entrega, pk=pk, estudiante=perfil)
    versiones = entrega.versiones.prefetch_related('evidencias').all()
    evidencias = entrega.evidencias.all()
    return render(request, 'entregas/detalle_entrega.html', {
        'entrega': entrega, 'versiones': versiones, 'evidencias': evidencias,
    })


@login_required
@estudiante_required
def reentregar_entrega(request, pk):
    perfil = Perfil.objects.get(usuario=request.user, rol='ESTUDIANTE')
    entrega = get_object_or_404(Entrega, pk=pk, estudiante=perfil)
    if request.method == 'POST':
        form = VersionEntregaForm(request.POST, request.FILES)
        if form.is_valid():
            version = form.save(commit=False)
            version.entrega = entrega
            version.estado = 'REENTREGADA'
            resultados = validate_submission(
                form.cleaned_data['archivo'],
                form.cleaned_data['repositorio_github'],
                entrega.actividad,
                perfil,
            )
            try:
                raise_for_failed_validations(resultados)
            except ValidationError as error:
                form.add_error(None, error)
            else:
                version.hash_archivo = resultados['hash_archivo']
                version.save()
                save_validation_evidence(resultados, version=version)
                entrega.estado = 'REENTREGADA'
                entrega.observaciones = form.cleaned_data.get('comentario', '')
                entrega.save()
                return redirect('entregas_estudiante:detalle_entrega', pk=entrega.pk)
    else:
        form = VersionEntregaForm()
    return render(request, 'entregas/reentregar_entrega.html', {'form': form, 'entrega': entrega})


@login_required
@docente_required
def lista_entregas_docente(request):
    context = _entregas_docente_context(request)
    if request.GET.get('export') == 'csv':
        return export_entregas_csv(context['entregas'])

    return render(
        request,
        'entregas/lista_entregas_docente.html',
        context,
    )


@login_required
@docente_required
def reporte_entregas_docente(request):
    return render(
        request,
        'entregas/reporte_entregas.html',
        _entregas_docente_context(request),
    )


@login_required
@docente_required
def crear_actividad(request):
    if request.method == 'POST':
        form = ActividadForm(request.user, request.POST)
        if form.is_valid():
            actividad = form.save(commit=False)
            actividad.creado_por = request.user
            actividad.save()
            return redirect('entregas_docente:lista_entregas_docente')
    else:
        form = ActividadForm(request.user)
    return render(request, 'entregas/crear_actividad.html', {'form': form})


@login_required
@docente_required
def detalle_entrega_docente(request, pk):
    entrega = get_object_or_404(Entrega, pk=pk)
    return render(request, 'entregas/detalle_entrega_docente.html', {'entrega': entrega})
