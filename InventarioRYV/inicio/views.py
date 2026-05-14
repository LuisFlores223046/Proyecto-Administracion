"""
Archivo: views.py
Descripción: Vistas para la página de inicio pública del sistema RYV Rentas.
             Gestiona la vista de bienvenida accesible sin autenticación,
             según lo definido en RF-04 y HU-001 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.shortcuts import render, redirect


def landing(request):
    """
    @brief Muestra la página de inicio pública de RYV Rentas.

    @details Si el usuario ya tiene una sesión activa, redirige directamente
    al listado de rentas. En caso contrario, muestra la página pública
    con información general de la empresa, catálogo de maquinaria y
    datos de contacto, según RF-04 del SRS.

    @param request HttpRequest Solicitud HTTP.

    @return HttpResponse Redirige al listado de rentas si el usuario está
    autenticado, o renderiza la plantilla inicio/landing.html si no lo está.
    """
    if request.user.is_authenticated:
        return redirect('rentas:lista')
    return render(request, 'inicio/landing.html')
