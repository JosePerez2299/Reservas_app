
from django_select2.forms import Select2Widget


class UsuarioWidget(Select2Widget):
    def build_attrs(self, *args, **kwargs):
        attrs = super().build_attrs(*args, **kwargs)
        attrs.update({
            'data-placeholder': 'Buscar usuario...',
            'data-minimum-input-length': 2,
            'data-language': 'es',
            'data-allow-clear': 'true',
            'data-minimum-results-for-search': 1,
            'data-close-on-select': 'true',
        })
        return attrs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = []
        self.attrs = self.build_attrs(self.attrs)

