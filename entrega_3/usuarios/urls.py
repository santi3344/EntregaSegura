from django.urls import path

from . import views


urlpatterns = [

    # Inicio de sesión
    path(
        '',
        views.login_usuario,
        name='login'
    ),

    path(
        'registro/docente/',
        views.registro_docente,
        name='registro_docente'
    ),

    path(
        'registro/docente/verificar/<uuid:registro_id>/',
        views.verificar_registro_docente,
        name='verificar_registro_docente'
    ),

    # Página de inicio
    path(
        'inicio/',
        views.inicio,
        name='inicio'
    ),

    # Panel del docente
    path(
        'docente/',
        views.panel_docente,
        name='panel_docente'
    ),

    # Panel del estudiante
    path(
        'estudiante/',
        views.panel_estudiante,
        name='panel_estudiante'
    ),

    path(
        'estudiante/cursos/',
        views.mis_cursos,
        name='mis_cursos'
    ),

    path(
        'estudiante/grupos/',
        views.mis_grupos,
        name='mis_grupos'
    ),

    # Cerrar sesión
    path(
        'logout/',
        views.cerrar_sesion,
        name='logout'
    ),
]