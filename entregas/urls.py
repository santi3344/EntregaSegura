from django.urls import path

from . import views

app_name = 'entregas_estudiante'

urlpatterns = [
    path('entregas/', views.mis_entregas, name='mis_entregas'),
    path('entregas/nueva/', views.crear_entrega, name='crear_entrega'),
    path('entregas/<int:pk>/', views.detalle_entrega, name='detalle_entrega'),
    path('entregas/<int:pk>/reentregar/', views.reentregar_entrega, name='reentregar_entrega'),
]
