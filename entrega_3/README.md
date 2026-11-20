# Entrega 3 — EntregaSegura

Esta carpeta contiene la versión completa correspondiente al cierre de la
Entrega 3. Incluye el código actualizado de la aplicación, pruebas,
configuración de producción, respaldos y documentación.

## Contenido

- `EntregaSegura/`: configuración Django y configuración de producción.
- `usuarios/`: autenticación, roles, registro docente por correo y creación de
  estudiantes.
- `cursos/`: cursos y grupos académicos.
- `entregas/`: actividades, entregas, validaciones, reentregas, reportes y
  descargas protegidas.
- `backups/`: scripts de respaldo y restauración.
- `docs/`: evidencia, manual, documentación técnica, informe de vulnerabilidades,
  sustentación y políticas en Markdown y Word.

## Funcionalidades incluidas

- Panel docente con filtros, CSV y reporte imprimible.
- Validación de archivo, integridad, metadatos y GitHub opcional.
- Versionado de reentregas.
- Actividades pendientes visibles para estudiantes.
- Descarga protegida de archivos originales y versiones.
- Registro docente con verificación por correo.
- Creación de estudiantes con cambio obligatorio de contraseña temporal.
- Despliegue en Railway con PostgreSQL, HTTPS y respaldos.

## Ejecución local

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

No se incluyen secretos, la base de datos local ni archivos cargados de
usuarios. Las variables necesarias deben configurarse a partir de `.env.example`.
