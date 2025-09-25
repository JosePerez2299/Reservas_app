# usuarios/management/commands/create_sample_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from django.db import transaction, IntegrityError
from django.core.mail import send_mail


class Command(BaseCommand):
    help = "Crea 4 usuarios de ejemplo: 2 usuarios en el grupo 'usuario' y 2 en 'administrador'."

    def handle(self, *args, **options):
        subject = "Confirmación de Reserva del usuario admin1"
        message = f"Estimado .\nSu reserva con ID  ha sido creada y está pendiente de aprobación"
        recipient_list = ["16-10882+admin1@usb.ve"]
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
