from import_export import resources
from reservas.models import Usuario

class UsuarioResource(resources.ModelResource):
    class Meta:
        model = Usuario
        # Si quieres exportar sólo algunos campos:
        fields = ('id', 'username', 'email', 'ubicacion', 'piso')
        export_order = ('id', 'username', 'email', 'ubicacion', 'piso')
