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

## Limitaciones pendientes

No se declara producción terminada porque todavía faltan proveedor, dominio,
DNS, certificado TLS, almacenamiento persistente, SMTP y programación de
respaldos remotos.
