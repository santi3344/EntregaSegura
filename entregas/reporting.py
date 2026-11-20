import csv

from django.http import HttpResponse


def export_entregas_csv(entregas):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reporte_entregas.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow([
        'Estudiante', 'Actividad', 'Curso', 'Estado', 'Fecha de entrega',
        'Repositorio GitHub', 'Versiones', 'Validaciones aprobadas',
    ])
    for entrega in entregas:
        evidencias = list(entrega.evidencias.all())
        writer.writerow([
            entrega.estudiante.usuario.username,
            entrega.actividad.titulo,
            entrega.actividad.curso.nombre,
            entrega.get_estado_display(),
            entrega.fecha_entrega.strftime('%Y-%m-%d %H:%M'),
            entrega.repositorio_github,
            entrega.versiones.count(),
            sum(evidencia.aprobado for evidencia in evidencias),
        ])
    return response
