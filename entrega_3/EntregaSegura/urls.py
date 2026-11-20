from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),
    path('docente/', include('cursos.urls')),
    path('estudiante/', include('entregas.urls')),
    path('docente/entregas/', include('entregas.docente_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)