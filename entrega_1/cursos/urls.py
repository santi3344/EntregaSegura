from django.urls import path

from . import views

app_name = 'cursos'

urlpatterns = [
    path('cursos/', views.lista_cursos, name='lista_cursos'),
    path('cursos/<int:pk>/editar/', views.editar_curso, name='editar_curso'),
    path('cursos/<int:pk>/eliminar/', views.eliminar_curso, name='eliminar_curso'),
    path('grupos/', views.lista_grupos, name='lista_grupos'),
    path('grupos/<int:pk>/editar/', views.editar_grupo, name='editar_grupo'),
    path('grupos/<int:pk>/eliminar/', views.eliminar_grupo, name='eliminar_grupo'),
]
