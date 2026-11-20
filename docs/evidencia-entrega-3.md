# Evidencia de Entrega 3

**Proyecto:** EntregaSegura  
**Fecha de verificación:** 19 de noviembre de 2026

## Pruebas ejecutadas

| Control | Comando | Resultado |
|---|---|---|
| Configuración Django | `python manage.py check` | PASS: sin errores |
| Suite completa | `python manage.py test` | PASS: 30 pruebas aprobadas |
| Sintaxis Python | `python -m compileall -q EntregaSegura cursos entregas usuarios` | PASS |
| Configuración de despliegue | `python manage.py check --deploy --settings=EntregaSegura.production` | PASS con variables de validación; falta probar con el dominio real |

## Funcionalidades verificadas

- Panel docente con filtros por curso, actividad, estado, estudiante y rango
  de fechas.
- Descarga de entregas en CSV.
- Reporte HTML imprimible y guardable como PDF.
- Aislamiento de resultados por docente autenticado.
- Validaciones de archivos, integridad, metadatos y repositorio GitHub.
- Versionado de reentregas.

## Seguridad implementada

- `SECRET_KEY` obligatorio en configuración de producción.
- `DEBUG=False` en producción.
- Redirección HTTPS y cookies seguras.
- HSTS, `X-Frame-Options`, `nosniff` y política de referencia.
- Protección CSRF y autorización por rol.
- Validación de extensión, tamaño, contenido no vacío y SHA-256.

## Respaldo local

El script `backups/backup_sqlite.ps1` crea una copia fechada de la base de
datos y comprime `media/` cuando existe. La restauración debe probarse siempre
sobre una copia, nunca sobre la base de producción. La prueba local realizada
creó un respaldo y obtuvo `PRAGMA integrity_check: ok`.

## Respaldo de producción

El repositorio incluye `backups/backup_production.ps1`, que genera un respaldo
custom de PostgreSQL y un archivo comprimido de `media/`, con retención
configurable. `backups/restore_production.ps1` restaura el respaldo en una base
de datos de prueba. El respaldo administrado de PostgreSQL debe activarse en el
panel de Railway y la prueba de restauración debe registrarse con fecha,
responsable y resultado.

## Pendientes no programables

Quedan la aprobación institucional de la política de datos, la activación del
respaldo administrado en Railway y la sustentación del proyecto.
