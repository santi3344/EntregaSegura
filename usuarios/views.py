import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from cursos.models import Curso, Grupo

from .forms import RegistroDocenteForm
from .models import Perfil, RegistroDocentePendiente


# ==========================================
# LOGIN
# ==========================================

@ensure_csrf_cookie
def login_usuario(request):

    # Si ya está autenticado, enviarlo según su rol
    if request.user.is_authenticated:
        return redireccionar_por_rol(request.user)

    if request.method == 'POST':

        username = request.POST.get('usuario', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            return render(request, 'usuarios/login.html', {
                'error': 'El usuario y la contraseña son obligatorios.',
            })
        if len(username) > 150:
            return render(request, 'usuarios/login.html', {
                'error': 'El usuario no puede superar los 150 caracteres.',
            })
        if len(password) > 128:
            return render(request, 'usuarios/login.html', {
                'error': 'La contraseña no puede superar los 128 caracteres.',
            })
        if any(ord(char) < 32 for char in username + password):
            return render(request, 'usuarios/login.html', {
                'error': 'El usuario o la contraseña contienen caracteres inválidos.',
            })

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


def registro_docente(request):
    if request.user.is_authenticated:
        return redireccionar_por_rol(request.user)

    form = RegistroDocenteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        RegistroDocentePendiente.objects.filter(
            expira_en__lte=timezone.now(),
        ).delete()
        if RegistroDocentePendiente.objects.filter(
            email__iexact=form.cleaned_data['email'],
        ).exists():
            return render(request, 'usuarios/registro_docente.html', {
                'form': form,
                'error': (
                    'Ya existe una verificación pendiente para ese correo. '
                    'Usa el código enviado o espera a que venza.'
                ),
            })

        codigo = f'{secrets.randbelow(1_000_000):06d}'
        usuario = form.save(commit=False)
        pendiente = RegistroDocentePendiente.objects.create(
            username=usuario.username,
            email=usuario.email,
            first_name=usuario.first_name,
            last_name=usuario.last_name,
            password_hash=usuario.password,
            codigo_hash=make_password(codigo),
            expira_en=timezone.now() + timedelta(minutes=10),
        )

        try:
            send_mail(
                subject='Código de verificación de EntregaSegura',
                message=(
                    f'Hola {usuario.first_name or usuario.username},\n\n'
                    f'Tu código de verificación es: {codigo}\n'
                    'Vence en 10 minutos. Si no solicitaste esta cuenta, '
                    'puedes ignorar este mensaje.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
        except Exception:
            pendiente.delete()
            return render(request, 'usuarios/registro_docente.html', {
                'form': form,
                'error': (
                    'No se pudo enviar el correo. Verifica la configuración '
                    'del servicio de correo e inténtalo nuevamente.'
                ),
            })

        return redirect('verificar_registro_docente', registro_id=pendiente.pk)

    return render(request, 'usuarios/registro_docente.html', {'form': form})


def verificar_registro_docente(request, registro_id):
    pendiente = get_object_or_404(RegistroDocentePendiente, pk=registro_id)

    if pendiente.expira_en <= timezone.now():
        pendiente.delete()
        return render(request, 'usuarios/verificar_registro_docente.html', {
            'expirado': True,
        })

    if pendiente.intentos >= 5:
        pendiente.delete()
        return render(request, 'usuarios/verificar_registro_docente.html', {
            'bloqueado': True,
        })

    error = None
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        codigo_formato_valido = (
            codigo.isascii() and codigo.isdigit() and len(codigo) == 6
        )

        if not codigo_formato_valido or not check_password(codigo, pendiente.codigo_hash):
            pendiente.intentos += 1
            pendiente.save(update_fields=['intentos'])
            if pendiente.intentos >= 5:
                pendiente.delete()
                return render(request, 'usuarios/verificar_registro_docente.html', {
                    'bloqueado': True,
                })
            error = 'El código no es correcto. Revisa tu correo e inténtalo de nuevo.'
        else:
            try:
                with transaction.atomic():
                    pendiente = RegistroDocentePendiente.objects.select_for_update().get(
                        pk=registro_id
                    )
                    if pendiente.expira_en <= timezone.now():
                        pendiente.delete()
                        return render(request, 'usuarios/verificar_registro_docente.html', {
                            'expirado': True,
                        })
                    if User.objects.filter(username__iexact=pendiente.username).exists():
                        pendiente.delete()
                        return render(request, 'usuarios/verificar_registro_docente.html', {
                            'error': 'No se pudo completar el registro. Inicia el proceso nuevamente.',
                        })

                    usuario = User(
                        username=pendiente.username,
                        email=pendiente.email,
                        first_name=pendiente.first_name,
                        last_name=pendiente.last_name,
                        password=pendiente.password_hash,
                    )
                    usuario.save()
                    Perfil.objects.create(usuario=usuario, rol='DOCENTE')
                    pendiente.delete()
            except IntegrityError:
                return render(request, 'usuarios/verificar_registro_docente.html', {
                    'error': 'No se pudo completar el registro. Inicia el proceso nuevamente.',
                })

            messages.success(request, 'Correo verificado. Ya puedes iniciar sesión como docente.')
            return redirect('login')

    return render(request, 'usuarios/verificar_registro_docente.html', {
        'error': error,
        'correo': pendiente.email,
        'registro_id': pendiente.pk,
    })


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