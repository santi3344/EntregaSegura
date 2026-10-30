from django.urls import path

from . import views

app_name = 'entregas_docente'

urlpatterns = [
    path('', views.lista_entregas_docente, name='lista_entregas_docente'),
    path('actividades/nueva/', views.crear_actividad, name='crear_actividad'),
    path('entregas/<int:pk>/', views.detalle_entrega_docente, name='detalle_entrega_docente'),
]
