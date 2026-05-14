"""
Archivo: forms.py
Descripción: Formularios para el módulo de inventario del sistema RYV Rentas.
             Define los formularios de creación y edición de equipos, así como
             el formulario de solicitudes de cambio enviadas por el Empleado,
             según lo definido en RF-05 al RF-12 y RN-007, RN-008 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""

from django import forms
from .models import Equipo


class EquipoForm(forms.ModelForm):
    """
    @brief Formulario para crear o editar un equipo del inventario.

    @details Valida que las unidades en mantenimiento no sean iguales o mayores
    a la cantidad total registrada, según lo definido en RF-05 y RF-09 del SRS.
    """

    class Meta:
        model = Equipo
        fields = [
            'nombre',
            'descripcion',
            'imagen',
            'cantidad_total',
            'cantidad_en_mantenimiento',
        ]
        widgets = {
            'nombre': forms.TextInput(
                attrs={'class': 'input-campo'}
            ),
            'descripcion': forms.Textarea(
                attrs={'class': 'input-campo', 'rows': 3}
            ),
            'imagen': forms.ClearableFileInput(
                attrs={'class': 'input-campo input-campo--file'}
            ),
            'cantidad_total': forms.NumberInput(
                attrs={'class': 'input-campo', 'min': 1}
            ),
            'cantidad_en_mantenimiento': forms.NumberInput(
                attrs={'class': 'input-campo', 'min': 0}
            ),
        }
        labels = {
            'nombre': 'Nombre del equipo',
            'descripcion': 'Descripción',
            'imagen': 'Imagen de referencia (opcional)',
            'cantidad_total': 'Cantidad total de unidades',
            'cantidad_en_mantenimiento': 'Unidades en mantenimiento',
        }
        help_texts = {
            'cantidad_en_mantenimiento': (
                'Unidades que están fuera de servicio temporalmente.'
            ),
            'imagen': (
                'Foto de referencia del equipo (jpg, png, etc.).'
            ),
        }

    def clean(self):
        """
        @brief Valida que las unidades en mantenimiento no superen la cantidad total.

        @return dict Los datos limpios del formulario si la validación es exitosa.

        @raise ValidationError Si cantidad_en_mantenimiento es igual o mayor
        a cantidad_total.
        """
        cleaned = super().clean()
        total = cleaned.get('cantidad_total')
        mant = cleaned.get('cantidad_en_mantenimiento')
        if total is not None and mant is not None:
            if mant >= total:
                raise forms.ValidationError(
                    'Las unidades en mantenimiento no pueden ser '
                    'iguales o mayores a la cantidad total.'
                )
        return cleaned


class SolicitudEquipoForm(forms.Form):
    """
    @brief Formulario para que el Empleado solicite cambios en el inventario.

    @details Permite solicitar el alta de un nuevo equipo, la edición de uno existente
    o su baja. Los campos requeridos se validan dinámicamente según el tipo
    de solicitud seleccionado, cumpliendo con RN-008 del SRS.
    """

    TIPO_CHOICES = [
        ('alta_equipo', 'Alta de nuevo equipo'),
        ('edicion_equipo', 'Edición de equipo existente'),
        ('baja_equipo', 'Baja de equipo'),
    ]

    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        label='Tipo de solicitud',
        widget=forms.Select(attrs={'class': 'input-campo', 'id': 'id_tipo_solicitud'}),
    )

    equipo_existente = forms.ModelChoiceField(
        queryset=Equipo.objects.none(),
        required=False,
        label='Equipo a modificar / dar de baja',
        empty_label='— Selecciona un equipo —',
        widget=forms.Select(attrs={'class': 'input-campo', 'id': 'id_equipo_existente'}),
    )

    nombre_equipo = forms.CharField(
        label='Nombre del equipo',
        required=False,
        widget=forms.TextInput(attrs={'class': 'input-campo', 'placeholder': 'Ej. Taladro percutor 18V'}),
    )
    descripcion_equipo = forms.CharField(
        label='Descripción',
        required=False,
        widget=forms.Textarea(attrs={'class': 'input-campo', 'rows': 3,
                                     'placeholder': 'Características, marca, modelo...'}),
    )
    cantidad_total = forms.IntegerField(
        label='Cantidad de unidades',
        required=False,
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'input-campo', 'min': 1}),
    )

    cantidad_baja = forms.IntegerField(
        label='Cantidad de unidades a dar de baja',
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'input-campo', 'min': 1}),
        help_text='Número de unidades que deseas retirar del inventario.',
    )

    comentario = forms.CharField(
        label='Motivo / observaciones',
        widget=forms.Textarea(
            attrs={'class': 'input-campo', 'rows': 3,
                   'placeholder': 'Explica el motivo de la solicitud...'}
        ),
    )

    def __init__(self, *args, **kwargs):
        """
        @brief Inicializa el formulario cargando los equipos activos disponibles
        para selección en los campos de edición y baja.

        @param args tuple Argumentos posicionales del formulario.
        @param kwargs dict Argumentos de palabras clave del formulario.
        """
        super().__init__(*args, **kwargs)
        self.fields['equipo_existente'].queryset = Equipo.objects.filter(
            activo=True
        ).order_by('nombre')

    def clean(self):
        """
        @brief Valida los campos requeridos según el tipo de solicitud seleccionado.

        @details Para alta de equipo valida que se ingrese nombre y cantidad. Para
        edición y baja valida que se seleccione un equipo existente. Para
        baja además valida que se indique la cantidad de unidades a retirar.

        @return dict Los datos limpios del formulario si la validación es exitosa.

        @raise ValidationError Por campo específico si algún dato requerido
        según el tipo de solicitud está ausente o es inválido.
        """
        cleaned = super().clean()
        tipo = cleaned.get('tipo')

        if tipo == 'alta_equipo':
            if not cleaned.get('nombre_equipo', '').strip():
                self.add_error(
                    'nombre_equipo',
                    'El nombre del equipo es obligatorio para una alta.',
                )
            if not cleaned.get('cantidad_total'):
                self.add_error(
                    'cantidad_total',
                    'La cantidad de unidades es obligatoria.',
                )

        elif tipo == 'edicion_equipo':
            if not cleaned.get('equipo_existente'):
                self.add_error(
                    'equipo_existente',
                    'Debes seleccionar un equipo.',
                )

        elif tipo == 'baja_equipo':
            if not cleaned.get('equipo_existente'):
                self.add_error(
                    'equipo_existente',
                    'Debes seleccionar un equipo.',
                )
            if not cleaned.get('cantidad_baja'):
                self.add_error(
                    'cantidad_baja',
                    'Debes indicar cuántas unidades deseas dar de baja.',
                )

        return cleaned
