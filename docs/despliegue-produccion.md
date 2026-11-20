# Despliegue, dominio y respaldos

## Estado

El repositorio contiene la configuración de producción y el script de respaldo,
pero el despliegue real todavía requiere un proveedor, dominio, DNS y
credenciales que no están disponibles en el repositorio.

## Checklist

1. Crear servicio de aplicación y base de datos.
2. Configurar las variables de `.env.example`.
3. Ejecutar `python manage.py migrate`.
4. Ejecutar `python manage.py collectstatic --noinput`.
5. Publicar mediante Gunicorn/Uvicorn detrás de HTTPS.
6. Apuntar DNS del dominio al proveedor.
7. Programar `backups/backup_sqlite.ps1` o el respaldo administrado del proveedor.
8. Probar restauración y documentar fecha, responsable y resultado.
9. Configurar monitoreo, logs y renovación del certificado.

Sin dominio y credenciales del proveedor no es posible afirmar que el sistema
está desplegado en producción.

## Bloqueo actual

Al 19 de noviembre de 2026 no se ha seleccionado proveedor ni dominio. Por
tanto, el código de producción está preparado, pero el despliegue real queda
pendiente de esas credenciales y de la configuración DNS.
