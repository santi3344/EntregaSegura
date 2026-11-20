![alt text](image.png)# Guion de sustentación — Entrega 3

## Diapositiva 1. Presentación

EntregaSegura es una plataforma para gestionar actividades, recibir archivos,
validar entregas y conservar evidencias de los controles aplicados.

## Diapositiva 2. Problema y solución

El sistema centraliza la recepción de trabajos, reduce errores manuales y
permite al docente consultar resultados mediante filtros y reportes.

## Diapositiva 3. Panel docente

Demostrar el acceso del docente, seleccionar curso, actividad, estado y rango
de fechas, aplicar filtros y descargar el CSV. Abrir el reporte imprimible y
mostrar la opción de guardarlo como PDF.

## Diapositiva 4. Validaciones

Explicar las cuatro capas: archivo, integridad, metadatos y repositorio GitHub.
Mostrar las evidencias almacenadas para cada entrega y explicar el resultado
aprobado o rechazado.

## Diapositiva 5. Seguridad

Presentar la separación de secretos mediante variables de entorno, `DEBUG`
desactivado en producción, HTTPS, cookies seguras, HSTS, CSRF, autorización
por roles y validación de archivos.

## Diapositiva 6. Pruebas

Indicar que `manage.py check` no reportó errores y que la suite completa
ejecutó 45 pruebas con 45 aprobadas. Mostrar también la prueba de descarga
protegida de archivos.

## Diapositiva 7. Documentación y datos personales

Presentar el manual de usuario, la documentación técnica y la política de
tratamiento de datos. Aclarar que la política requiere revisión institucional
o jurídica antes de su aprobación definitiva.

## Diapositiva 8. Estado de producción

Mostrar el despliegue público en Railway, el dominio activo y la pestaña de
copias de seguridad de PostgreSQL. Indicar que existe una copia de volumen y
un horario automático de respaldos. Aclarar que el respaldo de archivos
cargados debe conservarse en un almacenamiento persistente independiente.

## Cierre

La Entrega 3 programable está implementada y probada. Los pendientes restantes
son documentar una restauración de respaldo, obtener la aprobación
institucional de la política de datos y realizar la presentación.
