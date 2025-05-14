
from django_filters.views import FilterView

from reservas.library.filters.filters import create_generic_filterset

class ColumnsMixin:
    # Define una lista de tuplas (campo, etiqueta)
    list_display = []  # e.g. [('nombre','Nombre'), ('tipo','Tipo'), ...]

    def get_list_display(self):
        return self.list_display

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Cada entrada es {'name': campo, 'verbose': etiqueta}
        ctx['cols'] = [
            {'name': f, 'verbose': h}
            for f, h in self.get_list_display()
        ]

        meta = self.model._meta
        ctx['app_label']        = meta.app_label
        ctx['model_name_lower'] = meta.model_name

        return ctx
    

class AutoFilterMixin(FilterView):
    """
    Mixin que genera automáticamente un FilterSet basado en `list_display`.
    """
    filterset_class = None  # Lo genera si no se define

    def get_filterset_class(self):
        if self.filterset_class:
            return self.filterset_class
        
        model = self.get_queryset().model

        # Obtiene los campos desde list_display
        if hasattr(self, 'list_display'):
            field_names = [name for name, _ in self.list_display]
        else:
            field_names = [f.name for f in model._meta.fields if f.name != 'id']

        return create_generic_filterset(model=model, include_fields=field_names)
