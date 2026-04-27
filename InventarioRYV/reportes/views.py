"""
Archivo: views.py
Descripción: Vistas para el módulo de reportes del sistema RYV Rentas.
             Gestiona la generación y descarga de reportes PDF de inventario
             y rentas por periodo, así como el historial de reportes generados,
             según lo definido en RF-21 al RF-25 y RN-012 del SRS.
Fecha: 2026-04-26
Versión: 1.0
"""
import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import ReporteGenerado
from .forms import ReporteRentasForm
from .generators import generar_pdf_inventario, generar_pdf_rentas
from inventario.models import Equipo
from rentas.models import Renta
from authentication.decorators import admin_required


@admin_required
def panel_reportes(request):
    """
    Muestra el panel principal de generación de reportes.

    Presenta los formularios para generar reportes de inventario y de rentas
    por periodo, junto con los cinco reportes más recientes generados,
    según lo definido en RF-21, RF-22 y CU-22 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP.

    Retorna:
        HttpResponse: Renderiza la plantilla reportes/panel.html con el
        formulario de rentas y los reportes recientes.
    """
    form_rentas = ReporteRentasForm()
    reportes_recientes = ReporteGenerado.objects.select_related(
        'generado_por'
    )[:5]

    contexto = {
        'form_rentas': form_rentas,
        'reportes_recientes': reportes_recientes,
    }
    return render(request, 'reportes/panel.html', contexto)


@admin_required
def generar_inventario(request):
    """
    Genera y descarga el reporte PDF del estado actual del inventario.

    Consulta todos los equipos activos, genera el PDF y registra el reporte
    en el historial para su descarga posterior, según lo definido en RF-21
    y CU-23 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. Debe ser de método POST
        para ejecutar la generación del reporte.

    Retorna:
        HttpResponse: Descarga directa del archivo PDF si la generación
        es exitosa, o redirige al panel de reportes con mensaje de error
        si falla o si la solicitud no es POST.
    """
    if request.method == 'POST':
        try:
            equipos = Equipo.objects.filter(
                activo=True
            ).order_by('nombre')

            pdf_bytes = generar_pdf_inventario(equipos)

            nombre_archivo = (
                'inventario_'
                + datetime.date.today().strftime('%Y%m%d')
                + '.pdf'
            )

            ReporteGenerado.objects.create(
                tipo='inventario',
                generado_por=request.user,
                archivo_nombre=nombre_archivo,
            )

            response = HttpResponse(
                pdf_bytes,
                content_type='application/pdf',
            )
            response['Content-Disposition'] = (
                f'attachment; filename="{nombre_archivo}"'
            )
            return response

        except Exception:
            messages.error(
                request,
                'Error al generar el reporte de inventario.',
            )

    return redirect('reportes:panel')


@admin_required
def generar_rentas(request):
    """
    Genera y descarga el reporte PDF de rentas dentro de un periodo seleccionado.

    Filtra las rentas por el rango de fechas indicado, genera el PDF con el
    listado de rentas, precios e ingreso total del periodo, y registra el
    reporte en el historial, según lo definido en RF-22, RN-012 y CU-24 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. Debe ser de método POST con
        los campos periodo_inicio y periodo_fin del formulario de rentas.

    Retorna:
        HttpResponse: Descarga directa del archivo PDF si la generación
        es exitosa, o redirige al panel de reportes con mensaje de error
        si las fechas son inválidas o si ocurre un fallo en la generación.
    """
    if request.method == 'POST':
        form = ReporteRentasForm(request.POST)
        if form.is_valid():
            try:
                inicio = form.cleaned_data['periodo_inicio']
                fin = form.cleaned_data['periodo_fin']

                rentas = Renta.objects.filter(
                    fecha_inicio__gte=inicio,
                    fecha_inicio__lte=fin,
                ).select_related(
                    'equipo', 'cliente'
                ).order_by('fecha_inicio')

                pdf_bytes = generar_pdf_rentas(rentas, inicio, fin)

                nombre_archivo = (
                    'rentas_'
                    + inicio.strftime('%Y%m%d')
                    + '_'
                    + fin.strftime('%Y%m%d')
                    + '.pdf'
                )

                ReporteGenerado.objects.create(
                    tipo='rentas',
                    generado_por=request.user,
                    archivo_nombre=nombre_archivo,
                    periodo_inicio=inicio,
                    periodo_fin=fin,
                )

                response = HttpResponse(
                    pdf_bytes,
                    content_type='application/pdf',
                )
                response['Content-Disposition'] = (
                    f'attachment; filename="{nombre_archivo}"'
                )
                return response

            except Exception:
                messages.error(
                    request,
                    'Error al generar el reporte de rentas.',
                )
        else:
            messages.error(request, 'Fechas inválidas.')

    return redirect('reportes:panel')
