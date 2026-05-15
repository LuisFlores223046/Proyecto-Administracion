"""
Archivo: utils.py
Descripción: Funciones utilitarias para el módulo de rentas del sistema RYV Rentas.
             Provee funciones auxiliares para el mantenimiento automático del
             estado de las rentas, según lo definido en RN-004 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from datetime import date


def marcar_rentas_vencidas():
    """
    @brief Marca como 'vencidas' las rentas activas expiradas.

    @details Realiza una actualización masiva en la base de datos para evitar
    cargar cada instancia en memoria; pensado para ejecutarse desde tareas
    programadas (cron / Celery beat) y mantener consistente el estado de las rentas.

    @return int Número de registros actualizados a estado 'vencida'.
    """
    from .models import Renta
    vencidas = Renta.objects.filter(
        estado='activa',
        fecha_vencimiento__lt=date.today(),
    )
    count = vencidas.update(estado='vencida')
    return count
