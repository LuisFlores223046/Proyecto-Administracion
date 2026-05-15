"""
Archivo: models.py
Descripción: Modelos para el módulo de reportes del sistema RYV Rentas.
             Define el modelo ReporteGenerado que registra los metadatos
             de los reportes PDF generados por el Administrador, permitiendo
             su descarga posterior sin necesidad de regenerarlos desde cero,
             según lo definido en RF-21 al RF-25 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.db import models


class ReporteGenerado(models.Model):
    """
    @class ReporteGenerado
    @brief Registro de metadatos de un reporte PDF generado por el Administrador.

    @details No almacena el archivo físico, solo la información necesaria para
    identificarlo y regenerarlo bajo demanda desde el historial de reportes,
    según lo definido en RF-25 del SRS.

    @attributes
        tipo (str): Tipo de reporte generado ('inventario' o 'rentas').
        generado_por (Usuario): Usuario administrador que generó el reporte.
        fecha_generacion (datetime): Fecha y hora de creación del registro.
        periodo_inicio (date): Inicio del periodo reportado (solo aplica a rentas).
        periodo_fin (date): Fin del periodo reportado (solo aplica a rentas).
        archivo_nombre (str): Nombre del archivo PDF asociado al reporte.
    """

    TIPO_CHOICES = [
        ('inventario', 'Inventario'),
        ('rentas', 'Rentas por periodo'),
    ]
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='tipo de reporte',
    )
    generado_por = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='generado por',
    )
    fecha_generacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='fecha de generación',
    )
    periodo_inicio = models.DateField(
        null=True,
        blank=True,
        verbose_name='periodo inicio',
    )
    periodo_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name='periodo fin',
    )
    archivo_nombre = models.CharField(
        max_length=200,
        verbose_name='nombre de archivo',
    )

    class Meta:
        verbose_name = 'reporte generado'
        verbose_name_plural = 'reportes generados'
        ordering = ['-fecha_generacion']

    def __str__(self):
        """
        @brief Retorna la representación en texto del reporte generado.

        @return str Cadena con el tipo de reporte y la fecha y hora de generación
        en formato YYYY-MM-DD HH:MM.
        """
        return (
            f"{self.get_tipo_display()} — "
            f"{self.fecha_generacion.strftime('%Y-%m-%d %H:%M')}"
        )
