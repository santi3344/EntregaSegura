from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

from cursos.models import Curso, Grupo

from .models import Perfil


# ==========================================
# LOGIN
# ==========================================

@ensure_csrf_cookie
def login_usuario(request):

    # Si ya está autenticado, enviarlo según su rol
    if request.user.is_authenticated:
        return redireccionar_por_rol(request.user)

    if request.method == 'POST':

        username = request.POST.get('usuario')
        password = request.POST.get('password')

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        # Usuario y contraseña correctos
        if usuario is not None:

            login(request, usuario)

            return redireccionar_por_rol(usuario)

        # Usuario o contraseña incorrectos
        return render(
            request,
            'usuarios/login.html',
            {
                'error': 'Usuario o contraseña incorrectos.'
            }
        )

    # Mostrar login
    return render(
        request,
        'usuarios/login.html'
    )


# ==========================================
# REDIRECCIÓN SEGÚN ROL
# ==========================================

def redireccionar_por_rol(usuario):

    # Primero comprobar si es superusuario
    if usuario.is_superuser:
        return redirect('/admin/')

    try:

        perfil = Perfil.objects.get(
            usuario=usuario
        )

        # DOCENTE
        if perfil.rol == 'DOCENTE':
            return redirect('panel_docente')

        # ESTUDIANTE
        elif perfil.rol == 'ESTUDIANTE':
            return redirect('panel_estudiante')

    except Perfil.DoesNotExist:

        pass

    # Si no tiene perfil
    return redirect('inicio')


# ==========================================
# INICIO
# ==========================================

@login_required
def inicio(request):

    return render(
        request,
        'usuarios/inicio.html'
    )


# ==========================================
# PANEL DOCENTE
# ==========================================

@login_required
def panel_docente(request):

    try:

        perfil = Perfil.objects.get(
            usuario=request.user
        )

        # Si NO es docente
        if perfil.rol != 'DOCENTE':

            return redirect('inicio')

    except Perfil.DoesNotExist:

        return redirect('inicio')

    return render(
        request,
        'usuarios/docente.html',
        {
            'usuario': request.user,
            'perfil': perfil,
            'total_cursos': Curso.objects.filter(docente=request.user).count(),
            'total_grupos': Grupo.objects.filter(
                curso__docente=request.user
            ).count(),
        }
    )


# ==========================================
# PANEL ESTUDIANTE
# ==========================================

@login_required
def panel_estudiante(request):

    try:

        perfil = Perfil.objects.get(
            usuario=request.user
        )

        # Si NO es estudiante
        if perfil.rol != 'ESTUDIANTE':

            return redirect('inicio')

    except Perfil.DoesNotExist:

        return redirect('inicio')

    return render(
        request,
        'usuarios/estudiante.html',
        {
            'usuario': request.user,
            'perfil': perfil,
            'grupos': Grupo.objects.filter(
                estudiantes=perfil
            ).select_related('curso').order_by('curso__nombre', 'nombre'),
            'cursos': Curso.objects.filter(
                grupos__estudiantes=perfil
            ).distinct().order_by('nombre'),
        }
    )


@login_required
def mis_cursos(request):
    perfil = Perfil.objects.filter(
        usuario=request.user,
        rol='ESTUDIANTE',
    ).first()
    if perfil is None:
        return redirect('inicio')

    cursos = Curso.objects.filter(
        grupos__estudiantes=perfil
    ).distinct().order_by('nombre')
    return render(request, 'usuarios/mis_cursos.html', {
        'cursos': cursos,
    })


@login_required
def mis_grupos(request):
    perfil = Perfil.objects.filter(
        usuario=request.user,
        rol='ESTUDIANTE',
    ).first()
    if perfil is None:
        return redirect('inicio')

    grupos = Grupo.objects.filter(
        estudiantes=perfil
    ).select_related('curso', 'curso__docente').order_by(
        'curso__nombre',
        'nombre',
    )
    return render(request, 'usuarios/mis_grupos.html', {
        'grupos': grupos,
    })


# ==========================================
# CERRAR SESIÓN
# ==========================================

@login_required
def cerrar_sesion(request):

    logout(request)

    return redirect('login')