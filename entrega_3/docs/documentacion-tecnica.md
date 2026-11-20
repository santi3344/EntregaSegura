# Documentación técnica

## Componentes

- `usuarios`: autenticación, registro docente y perfiles.
- `cursos`: cursos, grupos y asignación de estudiantes.
- `entregas`: actividades, entregas, versiones y evidencias.
- `validators.py`: controles de archivo, integridad, metadatos y GitHub.
- SQLite: persistencia local de desarrollo.
- `MEDIA_ROOT`: almacenamiento de archivos cargados.

## Flujo de entrega

El estudiante envía un formulario multipart. La vista obtiene el perfil y la
actividad permitida, ejecuta las cuatro validaciones, calcula SHA-256, guarda
la entrega y persiste una evidencia por capa. Las reentregas siguen el mismo
flujo y se relacionan con la entrega original.

## Producción

Usar `DJANGO_SETTINGS_MODULE=EntregaSegura.production`, variables del archivo
`.env.example`, HTTPS, un servidor WSGI/ASGI y almacenamiento persistente.
SQLite es adecuado para una instalación pequeña; para alta concurrencia se
recomienda migrar a PostgreSQL.
