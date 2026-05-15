"""
Archivo: decorators.py
Descripción: Decoradores de control de acceso para el sistema RYV Rentas.
             Define los decoradores utilizados para restringir el acceso
             a las vistas según el rol del usuario autenticado
             (Administrador o Empleado), siguiendo las reglas de negocio
             definidas en RF-03 y RN-008 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps


def admin_required(view_func):
    """
    @brief Restringe el acceso a una vista exclusivamente a usuarios con rol de Administrador.

    @details Requiere que el usuario esté autenticado. Si no lo está, redirige al login.
    Si está autenticado pero no es Administrador, lanza un error 403 (PermissionDenied).

    @param view_func callable La vista de Django que se quiere proteger.

    @return callable La vista original si el usuario es Administrador,
    una redirección al login si no está autenticado,
    o un error 403 si no tiene el rol requerido.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        """
        @brief Verifica que el usuario sea administrador antes de ejecutar la vista.

        @param request HttpRequest Solicitud HTTP con el usuario autenticado.
        @param args tuple Argumentos posicionales adicionales de la URL.
        @param kwargs dict Argumentos de palabras clave adicionales de la URL.

        @return HttpResponse Resultado de la vista protegida.

        @raise PermissionDenied Si el usuario autenticado no tiene rol de administrador.
        """
        if not request.user.es_administrador():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def empleado_o_admin(view_func):
    """
    @brief Restringe el acceso a una vista a cualquier usuario autenticado,
    sin distinción de rol (Administrador o Empleado).

    @details Si el usuario no está autenticado, redirige al login.
    No distingue entre roles; basta con tener sesión activa.

    @param view_func callable La vista de Django que se quiere proteger.

    @return callable La vista original si el usuario está autenticado,
    o una redirección al login si no lo está.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        """
        @brief Verifica que el usuario esté autenticado antes de ejecutar la vista.

        @param request HttpRequest Solicitud HTTP con el usuario autenticado.
        @param args tuple Argumentos posicionales adicionales de la URL.
        @param kwargs dict Argumentos de palabras clave adicionales de la URL.

        @return HttpResponse Resultado de la vista protegida.
        """
        return view_func(request, *args, **kwargs)
    return wrapper
