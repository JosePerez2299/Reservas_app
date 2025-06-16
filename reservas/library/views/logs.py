from auditlog.models import LogEntry
from reservas.library.mixins.helpers import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView
from django.conf import settings
from django.db.models import Case, When, Value, CharField
from django.contrib.contenttypes.models import ContentType
from reservas.models import *
class LogListView(LoginRequiredMixin, PermissionRequiredMixin, ListCrudMixin,  SmartOrderingMixin,ListView ):
    """
    Muestra una lista de logs con un formulario de filtrado
    """
    model = LogEntry    
    permission_required = 'auditlog.view_logentry'
    template_name = 'reservas/actividad_table.html'
    paginate_by = 10
    cols = {
        'id': 'ID',
        'actor': 'Actor',
        'object_id': 'Objeto',
        'object_repr': 'Recurso',
        'action_label': 'Acción',
        'tipo': 'Tipo',

        'timestamp': 'Fecha',
    }

    crud_urls = {
        'view': 'log_detail',
    }
    actions = True

    def get_queryset(self):

        user = self.request.user
        qs = user.get_logs()
        action = {
            LogEntry.Action.CREATE: 'Crear',
            LogEntry.Action.UPDATE: 'Actualizar',
            LogEntry.Action.DELETE: 'Eliminar',
        }
        qs = qs.annotate(
            action_label=Case(
                When(action=LogEntry.Action.CREATE, then=Value(action[LogEntry.Action.CREATE])),
                When(action=LogEntry.Action.UPDATE, then=Value(action[LogEntry.Action.UPDATE])),
                When(action=LogEntry.Action.DELETE, then=Value(action[LogEntry.Action.DELETE])),
                default=Value('-'),
                output_field=CharField()
            ),
            tipo=Case(
                When(content_type=ContentType.objects.get_for_model(Usuario), then=Value('Usuario')),
                When(content_type=ContentType.objects.get_for_model(Espacio), then=Value('Espacio')),
                When(content_type=ContentType.objects.get_for_model(Reserva), then=Value('Reserva')),
                default=Value('-'),
                output_field=CharField()
            ),
            object=Case(
                When(content_type=ContentType.objects.get_for_model(Usuario), then=Value('Usuario')),
                When(content_type=ContentType.objects.get_for_model(Espacio), then=Value('Espacio')),
                When(content_type=ContentType.objects.get_for_model(Reserva), then=Value('Reserva')),
                default=Value('-'),
                output_field=CharField()
            )
        )

        return qs


class LogDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Muestra los detalles de un log
    """
    model = LogEntry
    permission_required = 'auditlog.view_logentry'
    template_name = 'reservas/log_detail.html'
    
   