from django import template
from reservas.models import Reserva

register = template.Library()

@register.simple_tag(takes_context=True)
def contador_reservas_pendientes(context):

    if context['request'].user.is_ad:
        return Reserva.objects.filter(estado='pendiente').count()
    else:
        return Reserva.objects.filter(estado='pendiente', usuario=context['request'].user).count()