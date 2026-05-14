"""
Archivo: forms.py
Descripción: Formularios para el módulo de reportes del sistema RYV Rentas.
             Define el formulario de selección de periodo para la generación
             de reportes de rentas, según lo definido en RF-22, RF-23
             y RN-012 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django import forms


class ReporteRentasForm(forms.Form):
    """
    @brief Formulario para seleccionar el periodo de un reporte de rentas.

    @details Permite al Administrador definir el rango de fechas para generar
    el reporte de rentas por periodo, cumpliendo con RF-22 y RN-012 del SRS
    que requieren precio e ingreso total del periodo seleccionado.
    """

    periodo_inicio = forms.DateField(
        label='Fecha de inicio',
        widget=forms.DateInput(
            attrs={'class': 'input-campo', 'type': 'date'},
            format='%Y-%m-%d',
        ),
    )
    periodo_fin = forms.DateField(
        label='Fecha de fin',
        widget=forms.DateInput(
            attrs={'class': 'input-campo', 'type': 'date'},
            format='%Y-%m-%d',
        ),
    )

    def clean(self):
        """
        @brief Valida que la fecha de inicio sea anterior o igual a la fecha de fin.

        @return dict Los datos limpios del formulario si la validación es exitosa.

        @raise ValidationError Si la fecha de fin es anterior a la fecha de inicio.
        """
        cleaned = super().clean()
        inicio = cleaned.get('periodo_inicio')
        fin = cleaned.get('periodo_fin')
        if inicio and fin and fin < inicio:
            raise forms.ValidationError(
                'La fecha de fin debe ser posterior a la fecha de inicio.'
            )
        return cleaned
