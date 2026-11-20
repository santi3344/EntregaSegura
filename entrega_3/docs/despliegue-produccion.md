# Despliegue, dominio y respaldos

## Estado

La aplicación está desplegada en Railway con PostgreSQL y dominio público.
Los respaldos administrados deben activarse desde el panel de Railway. El
repositorio incluye scripts para respaldar y restaurar PostgreSQL y `media/`
fuera del servicio.

## Checklist

1. Crear servicio de aplicación y base de datos.
2. Configurar las variables de `.env.example`.
3. Ejecutar `python manage.py migrate`.
4. Ejecutar `python manage.py collectstatic --noinput`.
5. Publicar mediante Gunicorn/Uvicorn detrás de HTTPS.
6. Apuntar DNS del dominio al proveedor.
7. Activar los respaldos de PostgreSQL en el panel de Railway.
8. Ejecutar `backups/backup_production.ps1` desde un equipo seguro o tarea programada,
   con `DATABASE_URL` configurada como secreto.
9. Probar la restauración sobre una base de datos de prueba con
   `backups/restore_production.ps1`; nunca sobre producción.
10. Documentar fecha, responsable, ubicación y resultado de la prueba.
11. Configurar monitoreo, logs y renovación del certificado.

### Variables para el respaldo externo

El script utiliza `DATABASE_URL` y no imprime su valor. Para restaurar se debe
usar una base de datos de prueba mediante `RESTORE_DATABASE_URL`.
