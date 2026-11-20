# Informe de análisis de vulnerabilidades

**Fecha:** 19 de noviembre de 2026  
**Alcance:** código Django, configuración y flujo de entregas.

## Hallazgos y correcciones

| ID | Severidad | Hallazgo | Corrección / estado |
|---|---|---|---|
| V-01 | Alta | `SECRET_KEY` estaba escrito en la configuración base. | Producción exige `DJANGO_SECRET_KEY`; se debe rotar la clave antes del despliegue. |
| V-02 | Alta | `DEBUG=True` en desarrollo no es seguro para producción. | `EntregaSegura.production` fuerza `DEBUG=False` salvo configuración explícita. |
| V-03 | Alta | Faltaban encabezados y cookies seguras de producción. | Se agregaron HTTPS, HSTS, cookies Secure, `X_FRAME_OPTIONS` y `nosniff`. |
| V-04 | Media | La consulta externa de GitHub podía fallar por red. | Se usa timeout, validación estricta de dominio y mensajes explícitos. |
| V-05 | Media | Archivos cargados requieren controles de tipo y tamaño. | Se validan extensión, tamaño, archivo no vacío e integridad SHA-256. |

## Controles adicionales

- Protección CSRF de Django.
- Autorización por rol y pertenencia a curso.
- Prevención de entregas iniciales duplicadas.
- Validación de datos y fechas en formularios.
- No se guardan contraseñas en texto plano.

## Pendientes antes de producción

- El escaneo local con `pip-audit 2.10.1` no encontró vulnerabilidades conocidas;
  el resultado está en `docs/cve-report-1.json`. Debe repetirse en CI.
- Configurar dominio, certificado TLS, SMTP y almacenamiento persistente.
- Revisar la política con el responsable jurídico.
- Rotar cualquier secreto histórico que haya sido expuesto.
