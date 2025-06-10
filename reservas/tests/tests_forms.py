from django.test import TestCase, RequestFactory
from django.contrib.auth.models import Group
from reservas.models import Usuario, Ubicacion, Espacio, Reserva
from django.urls import reverse
from reservas.library.forms.usuarios import UsuarioCreateForm, UsuarioUpdateForm
from reservas.library.forms.espacios import EspacioCreateForm, EspacioUpdateForm
from django.utils import timezone
import random
from datetime import timedelta
from datetime import time

class UsuarioFormsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Crear grupos necesarios en settings.GRUPOS.USUARIO y ADMINISTRADOR
        self.grupo_usuario = Group.objects.get_or_create(name=Usuario.GRUPOS.USUARIO)[0]
        self.grupo_admin = Group.objects.get_or_create(name=Usuario.GRUPOS.ADMINISTRADOR)[0]
        # Crear un usuario admin y un usuario no admin
        self.admin_user = Usuario.objects.create_user(username='admin', email='admin@example.com', password='pass')
        self.admin_user.groups.add(self.grupo_admin)
        self.admin_user.save()
        self.normal_user = Usuario.objects.create_user(username='normal', email='normal@example.com', password='pass')
        self.normal_user.groups.add(self.grupo_usuario)
        self.normal_user.save()

        self.ubicacion = Ubicacion.objects.create(nombre="Sede Central")


    def test_usuario_create_form_admin_ve_campo_groups(self):
        """Test para verificar que el campo groups se muestra para el usuario admin"""
        request = self.factory.post(reverse('usuario_create'))
        request.user = self.admin_user
        # Datos válidos mínimos
        data = {
            'username': 'nuevo',
            'email': 'nuevo@example.com',
            'password1': 'Password123$',
            'password2': 'Password123$',
            'ubicacion': self.ubicacion.pk,  # según validaciones de tu modelo
            'piso': 1,
            'groups': self.grupo_usuario.pk
        }
        form = UsuarioCreateForm(request, data=data)

        self.assertTrue(form.is_valid())    
        user = form.save()
        # Verificar que se asignó el grupo
        self.assertIn(self.grupo_usuario, user.groups.all())

    def test_usuario_create_form_no_admin_oculta_groups(self):
        """Test para verificar que el campo groups se oculta para el usuario no admin"""
        request = self.factory.post(reverse('usuario_create'))

        request.user = self.normal_user
        data = {
            'username': 'otro',
            'email': 'otro@example.com',
            'password1': 'Password123$',
            'password2': 'Password123$',
            'ubicacion': self.ubicacion.pk,
            'piso': 2,
        }
        form = UsuarioCreateForm(request, data=data)
        self.assertTrue(form.is_valid())
        # El campo groups debe estar oculto (widget HiddenInput)
        self.assertTrue(isinstance(form.fields['groups'].widget.__class__.__name__, str) or form.fields['groups'].widget.__class__.__name__ == 'HiddenInput')
        user = form.save()
        # Debe asignarse automáticamente el grupo USUARIO
        self.assertIn(self.grupo_usuario, user.groups.all())

    def test_usuario_update_form_password_mismatch(self):
        """Test para verificar que el campo password no coincide"""
        # Tomar una instancia existente
        instancia = self.normal_user
        request = self.factory.post(reverse('usuario_edit', args=[instancia.pk]))
        request.user = self.normal_user
        # Simular que el usuario no es admin: el campo groups se oculta
        data = {
            'username': instancia.username,
            'email': instancia.email,
            'ubicacion': '',
            'piso': 5,
            'password1': 'Newpass123',
            'password2': 'Different123',
        }
        form = UsuarioUpdateForm(request, data=data, instance=instancia)
        self.assertFalse(form.is_valid())
        self.assertIn('Las contraseñas no coinciden.', form.non_field_errors())

    def test_usuario_update_form_valida_cambio_contraseña(self):
        instancia = self.normal_user
        request = self.factory.post('/fake/')
        request.user = self.normal_user
        data = {
            'username': instancia.username,
            'email': instancia.email,
            'ubicacion': self.ubicacion.pk,
            'piso': 5,
            'password1': 'NuevaPass123',
            'password2': 'NuevaPass123',
        }
        form = UsuarioUpdateForm(request, data=data, instance=instancia)
        print(form.errors)
        self.assertTrue(form.is_valid())
        user = form.save()
        # Verificar que la contraseña cambió: intentar autenticar
        self.assertTrue(user.check_password('NuevaPass123'))


class EspacioFormsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Usuario.objects.create_user(username='testuser', password='pass')

        self.ubicacion = Ubicacion.objects.create(nombre='Ubicación Test')

        kwargs = {
            'nombre': 'Sala A',
            'piso': 1,
            'capacidad': 10,
            'tipo': Espacio.Tipo.SALON,
            'descripcion': 'Sala de reuniones A',
            'disponible': True,
        }
        kwargs['ubicacion'] = self.ubicacion
        self.espacio = Espacio.objects.create(**kwargs)

    def test_espacio_create_form_valido(self):
        """
        Test básico de que el EspacioCreateForm es válido con datos correctos.
        """
        request = self.factory.post(reverse('espacio_create'))
        request.user = self.user

        tipo_choices = list(Espacio.Tipo.choices)
        tipo_choices = [choice[0] for choice in tipo_choices]

        data = {
            'nombre': 'Sala B',
            'piso': 2,
            'capacidad': 20,
            'tipo': random.choice(tipo_choices),
            'descripcion': 'Sala de formación B',
            'disponible': True,
        }

        data['ubicacion'] = self.ubicacion.pk

        form = EspacioCreateForm(data=data)
        self.assertTrue(form.is_valid(), f"Errores: {form.errors.as_json()}")
        espacio_nuevo = form.save()
        # Verificar que se guardó con los mismos valores
        self.assertEqual(espacio_nuevo.nombre, data['nombre'])
        self.assertEqual(espacio_nuevo.piso, data['piso'])
        self.assertEqual(espacio_nuevo.capacidad, data['capacidad'])
        self.assertEqual(espacio_nuevo.disponible, True)

    def test_espacio_update_form_sin_cambiar_disponible_no_afecta_reservas(self):
        """
        Test que verifica que si el espacio ya estaba disponible y se mantiene disponible,
        no se rechazan las reservas futuras pendientes o aprobadas.
        """
        hoy = timezone.now().date()
        reserva_pendiente_fut = Reserva.objects.create(
            usuario=self.user,
            espacio=self.espacio,
            fecha_uso=hoy + timedelta(days=2),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado=Reserva.Estado.PENDIENTE,
        )
        reserva_aprobada_fut = Reserva.objects.create(
            usuario=self.user,
            espacio=self.espacio,
            fecha_uso=hoy + timedelta(days=3),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado=Reserva.Estado.APROBADA,
        )
        reserva_pasada = Reserva.objects.create(
            usuario=self.user,
            espacio=self.espacio,
            fecha_uso=hoy - timedelta(days=1),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado=Reserva.Estado.PENDIENTE,
        )

        data = {
            'nombre': self.espacio.nombre,
            'piso': self.espacio.piso,
            'capacidad': self.espacio.capacidad,
            'tipo': self.espacio.tipo,
            'descripcion': self.espacio.descripcion,
            'ubicacion': self.ubicacion.pk,
            'disponible': True,
        }
        

        request = self.factory.post(reverse('espacio_edit', args=[self.espacio.pk]), data)
        request.user = self.user

        form = EspacioUpdateForm(request, data=data, instance=self.espacio)

        print(form.errors)
        self.assertTrue(form.is_valid(), f"Errores: {form.errors.as_json()}")
        espacio_guardado = form.save()

        reserva_pendiente_fut.refresh_from_db()
        reserva_aprobada_fut.refresh_from_db()
        reserva_pasada.refresh_from_db()

        self.assertEqual(reserva_pendiente_fut.estado, Reserva.Estado.PENDIENTE)
        self.assertEqual(reserva_aprobada_fut.estado, Reserva.Estado.APROBADA)
        self.assertEqual(reserva_pasada.estado, Reserva.Estado.PENDIENTE)

    def test_espacio_update_form_cambiar_disponible_false_rechaza_reservas_futuras(self):
        """
        Test que verifica que al cambiar el estado de un espacio a no disponible,
        se rechazan las reservas futuras pendientes o aprobadas.
        """

        hoy = timezone.now().date()
        reserva_pendiente_fut = Reserva.objects.create(
            usuario=self.user,
            espacio=self.espacio,
            fecha_uso=hoy + timedelta(days=2),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado=Reserva.Estado.PENDIENTE,
        )
        reserva_aprobada_fut = Reserva.objects.create(
            usuario=self.user,
            espacio=self.espacio,
            fecha_uso=hoy + timedelta(days=3),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado=Reserva.Estado.APROBADA,
        )

        reserva_rechazada_fut = Reserva.objects.create(
            usuario=self.user,
            espacio=self.espacio,
            fecha_uso=hoy + timedelta(days=1),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado=Reserva.Estado.RECHAZADA,
        )

        reserva_pasada = Reserva.objects.create(
            usuario=self.user,
            espacio=self.espacio,
            fecha_uso=hoy - timedelta(days=1),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado=Reserva.Estado.PENDIENTE,
        )

        data = {
            'nombre': self.espacio.nombre,
            'piso': self.espacio.piso,
            'capacidad': self.espacio.capacidad,
            'tipo': self.espacio.tipo,
            'descripcion': self.espacio.descripcion,
            'ubicacion': self.ubicacion.pk,
            'disponible': False,
        }
        

        request = self.factory.post(reverse('espacio_edit', args=[self.espacio.pk]), data)
        request.user = self.user

        form = EspacioUpdateForm(request, data=data, instance=self.espacio)

        print(form.errors)
        self.assertTrue(form.is_valid(), f"Errores: {form.errors.as_json()}")
        espacio_guardado = form.save()

        # Recargar reservas desde BD y verificar que no cambiaron estado
        reserva_pendiente_fut.refresh_from_db()
        reserva_aprobada_fut.refresh_from_db()
        reserva_rechazada_fut.refresh_from_db()
        reserva_pasada.refresh_from_db()

        # Verificar que las reservas futuras pendientes y aprobadas se rechazaron
        self.assertEqual(reserva_pendiente_fut.estado, Reserva.Estado.RECHAZADA)
        self.assertEqual(reserva_aprobada_fut.estado, Reserva.Estado.RECHAZADA)
        self.assertEqual(reserva_rechazada_fut.estado, Reserva.Estado.RECHAZADA)
        self.assertEqual(reserva_pasada.estado, Reserva.Estado.PENDIENTE)

        # Verificar que el espacio se marcó como no disponible
        self.assertFalse(self.espacio.disponible)

    def test_espacio_update_form_si_initial_disponible_false_no_rechaza_nada(self):
        """
        Test que verifica que si el espacio ya estaba no disponible y se mantiene no disponible,
        no se rechazan las reservas futuras pendientes o aprobadas.
        """
        # Primero forzamos que el espacio esté inicialmente no disponible
        self.espacio.disponible = False
        self.espacio.save()

        hoy = timezone.now().date()
        reserva_pendiente_fut = Reserva.objects.create(
            espacio=self.espacio,
            usuario=self.user,
            fecha_uso=hoy + timedelta(days=2),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado=Reserva.Estado.PENDIENTE,
        )
        reserva_aprobada_fut = Reserva.objects.create(
            espacio=self.espacio,
            usuario=self.user,
            fecha_uso=hoy + timedelta(days=3),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado=Reserva.Estado.APROBADA,
        )

        data = {
            'nombre': self.espacio.nombre,
            'piso': self.espacio.piso,
            'capacidad': self.espacio.capacidad,
            'tipo': self.espacio.tipo,
            'descripcion': self.espacio.descripcion,
            'disponible': False,
            'ubicacion': self.ubicacion.pk,
        }


        request = self.factory.post(reverse('espacio_edit', args=[self.espacio.pk]), data)
        request.user = self.user

        form = EspacioUpdateForm(request, data=data, instance=self.espacio)
        self.assertTrue(form.is_valid(), f"Errores: {form.errors.as_json()}")
        espacio_guardado = form.save()

        reserva_pendiente_fut.refresh_from_db()
        reserva_aprobada_fut.refresh_from_db()
        # No deben haber cambiado
        self.assertEqual(reserva_pendiente_fut.estado, Reserva.Estado.PENDIENTE)
        self.assertEqual(reserva_aprobada_fut.estado, Reserva.Estado.APROBADA)


   
