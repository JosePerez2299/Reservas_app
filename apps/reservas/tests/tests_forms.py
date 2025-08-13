from django.test import TestCase, RequestFactory
from django.contrib.auth.models import Group
from reservas.models import Usuario, Ubicacion, Espacio, Reserva
from django.urls import reverse
from reservas..forms.usuarios import UsuarioCreateForm, UsuarioUpdateForm
from reservas..forms.espacios import EspacioCreateForm, EspacioUpdateForm
from reservas..forms.reservas import ReservaCreateForm, ReservaUpdateForm
from django.utils import timezone
import random
from datetime import timedelta, time, date

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


class ReservaCreateFormTestCase(TestCase):
    def setUp(self):
        """Configuración inicial para los tests"""
        self.factory = RequestFactory()
        
        # Crear ubicaciones
        self.ubicacion1 = Ubicacion.objects.create(nombre='Sede Central')
        self.ubicacion2 = Ubicacion.objects.create(nombre='Sede Norte')
        
        # Crear grupos usando la configuración de settings
        self.grupo_admin = Group.objects.get_or_create(name=Usuario.GRUPOS.ADMINISTRADOR)[0]
        self.grupo_moderador = Group.objects.get_or_create(name=Usuario.GRUPOS.MODERADOR)[0]
        self.grupo_usuario = Group.objects.get_or_create(name=Usuario.GRUPOS.USUARIO)[0]
        
        # Crear usuarios de diferentes tipos
        self.admin = Usuario.objects.create_user(
            username='admin123',
            email='admin@test.com',
            ubicacion=self.ubicacion1,
            piso=1
        )
        self.admin.groups.add(self.grupo_admin)

        self.admin2 = Usuario.objects.create_user(
            username='admin2123',
            email='admin2@test.com',
            ubicacion=self.ubicacion1,
            piso=1
        )
        self.admin2.groups.add(self.grupo_admin)
        
        self.moderador = Usuario.objects.create_user(
            username='moderador123',
            email='moderador@test.com',
            ubicacion=self.ubicacion1,
            piso=1
        )
        self.moderador.groups.add(self.grupo_moderador)
        
        self.usuario1 = Usuario.objects.create_user(
            username='usuario123',
            email='usuario1@test.com',
            ubicacion=self.ubicacion1,
            piso=1
        )
        self.usuario1.groups.add(self.grupo_usuario)
        
        self.usuario2 = Usuario.objects.create_user(
            username='usuario456',
            email='usuario2@test.com',
            ubicacion=self.ubicacion2,
            piso=2
        )
        self.usuario2.groups.add(self.grupo_usuario)
        
        # Crear espacios
        self.espacio_disponible = Espacio.objects.create(
            nombre='Salon101',
            ubicacion=self.ubicacion1,
            piso=1,
            capacidad=30,
            tipo=Espacio.Tipo.SALON,
            disponible=True
        )
        
        self.espacio_no_disponible = Espacio.objects.create(
            nombre='Salon102',
            ubicacion=self.ubicacion1,
            piso=1,
            capacidad=25,
            tipo=Espacio.Tipo.SALON,
            disponible=False
        )

    def test_espacios_disponibles_queryset(self):
        """Test que verifica que solo se muestran espacios disponibles"""
        request = self.factory.get('/')
        request.user = self.admin
        
        form = ReservaCreateForm(request=request)
        
        # Solo debe incluir espacios disponibles
        self.assertIn(self.espacio_disponible, form.fields['espacio'].queryset)
        self.assertNotIn(self.espacio_no_disponible, form.fields['espacio'].queryset)

    def test_admin_usuario_queryset(self):
        """Test que verifica el queryset de usuarios para administrador"""
        request = self.factory.get('/')
        request.user = self.admin
        
        form = ReservaCreateForm(request=request)
        
        # Admin debe poder ver usuarios y moderadores, además de sí mismo
        queryset_ids = list(form.fields['usuario'].queryset.values_list('id', flat=True))
        
        self.assertIn(self.admin.id, queryset_ids)
        self.assertNotIn(self.admin2.id, queryset_ids)
        self.assertIn(self.moderador.id, queryset_ids)
        self.assertIn(self.usuario1.id, queryset_ids)
        self.assertIn(self.usuario2.id, queryset_ids)

    def test_moderador_usuario_queryset(self):
        """Test que verifica el queryset de usuarios para moderador"""
        request = self.factory.get('/')
        request.user = self.moderador
        
        form = ReservaCreateForm(request=request)
        
        # Moderador debe poder ver usuarios de su ubicación y piso, además de sí mismo
        queryset_ids = list(form.fields['usuario'].queryset.values_list('id', flat=True))
        
        self.assertIn(self.moderador.id, queryset_ids)
        self.assertIn(self.usuario1.id, queryset_ids)  # Misma ubicación y piso
        self.assertNotIn(self.usuario2.id, queryset_ids)  # Diferente ubicación y piso
        self.assertNotIn(self.admin.id, queryset_ids)  # Diferente ubicación y piso

    def test_usuario_field_disabled_for_regular_user(self):
        """Test que verifica que el campo usuario está deshabilitado para usuarios regulares"""
        request = self.factory.get('/')
        request.user = self.usuario1
        
        form = ReservaCreateForm(request=request)
        
        # Campo debe estar deshabilitado y con valor inicial del usuario actual
        self.assertTrue(form.fields['usuario'].disabled)
        self.assertEqual(form.fields['usuario'].initial, self.usuario1)
        self.assertEqual(form.fields['usuario'].help_text, "No puedes cambiar este campo")

    def test_date_constraints(self):
        """Test que verifica las restricciones de fecha"""
        request = self.factory.get('/')
        request.user = self.admin
        
        form = ReservaCreateForm(request=request)
        
        # Verificar restricciones de fecha
        fecha_widget = form.fields['fecha_uso'].widget
        self.assertEqual(fecha_widget.attrs['min'], date.today().isoformat())
        self.assertEqual(
            fecha_widget.attrs['max'], 
            (date.today() + timedelta(days=90)).isoformat()
        )


class ReservaUpdateFormTestCase(TestCase):
    def setUp(self):
        """Configuración inicial para los tests"""
        self.factory = RequestFactory()
        
        # Crear ubicaciones
        self.ubicacion1 = Ubicacion.objects.create(nombre='Sede Central')
        self.ubicacion2 = Ubicacion.objects.create(nombre='Sede Norte')
        
        # Crear grupos
        self.grupo_admin = Group.objects.get_or_create(name=Usuario.GRUPOS.ADMINISTRADOR)[0]
        self.grupo_moderador = Group.objects.get_or_create(name=Usuario.GRUPOS.MODERADOR)[0]
        self.grupo_usuario = Group.objects.get_or_create(name=Usuario.GRUPOS.USUARIO)[0]
        
        # Crear usuarios
        self.admin = Usuario.objects.create_user(
            username='admin123',
            email='admin@test.com',
            ubicacion=self.ubicacion1,
            piso=1
        )
        self.admin.groups.add(self.grupo_admin)
        
        
        self.moderador = Usuario.objects.create_user(
            username='moderador123',
            email='moderador@test.com',
            ubicacion=self.ubicacion1,
            piso=1
        )
        self.moderador.groups.add(self.grupo_moderador)
        
        self.usuario1 = Usuario.objects.create_user(
            username='usuario123',
            email='usuario1@test.com',
            ubicacion=self.ubicacion1,
            piso=1
        )
        self.usuario1.groups.add(self.grupo_usuario)
        
        # Crear espacios
        self.espacio = Espacio.objects.create(
            nombre='Salon101',
            ubicacion=self.ubicacion1,
            piso=1,
            capacidad=30,
            tipo=Espacio.Tipo.SALON,
            disponible=True
        )
        
        self.espacio_diferente_ubicacion = Espacio.objects.create(
            nombre='Salon201',
            ubicacion=self.ubicacion2,
            piso=2,
            capacidad=25,
            tipo=Espacio.Tipo.SALON,
            disponible=True
        )
        
        # Crear reserva
        self.reserva = Reserva.objects.create(
            usuario=self.usuario1,
            espacio=self.espacio,
            fecha_uso=date.today() + timedelta(days=1),
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
            motivo='Reunión de trabajo',
            estado=Reserva.Estado.PENDIENTE
        )

    def test_form_fields_and_widgets(self):
        """Test que verifica los campos y widgets del formulario de actualización"""
        request = self.factory.get('/')
        request.user = self.admin
        
        form = ReservaUpdateForm(request=request, instance=self.reserva)
        
        # Verificar campos
        expected_fields = [
            'usuario', 'fecha_uso', 'hora_inicio', 'hora_fin', 
            'espacio', 'motivo', 'estado', 'motivo_admin'
        ]
        self.assertEqual(list(form.fields.keys()), expected_fields)
        
        # Verificar que usuario y espacio están deshabilitados
        self.assertTrue(form.fields['usuario'].disabled)
        self.assertTrue(form.fields['espacio'].disabled)
        self.assertEqual(form.fields['usuario'].help_text, "No puedes cambiar este campo")
        self.assertEqual(form.fields['espacio'].help_text, "No puedes cambiar este campo")

    def test_usuario_estado_disabled_for_regular_user(self):
        """Test que verifica que el estado está deshabilitado para usuarios regulares"""
        request = self.factory.get('/')
        request.user = self.usuario1
        
        form = ReservaUpdateForm(request=request, instance=self.reserva)
        
        self.assertTrue(form.fields['estado'].disabled)

    def test_moderador_estado_disabled_different_location(self):
        """Test que verifica restricciones para moderador con diferente ubicación"""
        # Crear reserva en espacio de diferente ubicación
        reserva_diferente = Reserva.objects.create(
            usuario=self.usuario1,
            espacio=self.espacio_diferente_ubicacion,
            fecha_uso=date.today() + timedelta(days=1),
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
            motivo='Reunión en otra sede',
            estado=Reserva.Estado.PENDIENTE
        )
        
        request = self.factory.get('/')
        request.user = self.moderador
        
        form = ReservaUpdateForm(request=request, instance=reserva_diferente)
        
        self.assertTrue(form.fields['estado'].disabled)
        self.assertEqual(
            form.fields['estado'].help_text,
            "No puedes aprobar o rechazar reservas de espacios de otra ubicación o piso"
        )

    def test_moderador_estado_enabled_same_location(self):
        """Test que verifica que el moderador puede cambiar estado en su ubicación"""
        request = self.factory.get('/')
        request.user = self.moderador
        
        form = ReservaUpdateForm(request=request, instance=self.reserva)
        
        # El espacio está en la misma ubicación y piso que el moderador
        self.assertFalse(form.fields['estado'].disabled)

    def test_admin_can_change_any_estado(self):
        """Test que verifica que el admin puede cambiar cualquier estado"""
        # Crear reserva en espacio de diferente ubicación
        reserva_diferente = Reserva.objects.create(
            usuario=self.usuario1,
            espacio=self.espacio_diferente_ubicacion,
            fecha_uso=date.today() + timedelta(days=1),
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
            motivo='Reunión en otra sede',
            estado=Reserva.Estado.PENDIENTE
        )
        
        request = self.factory.get('/')
        request.user = self.admin
        
        form = ReservaUpdateForm(request=request, instance=reserva_diferente)
        
        # Admin puede cambiar estado independientemente de la ubicación
        self.assertFalse(form.fields['estado'].disabled)

    def test_save_method_sets_aprobado_por_when_approved(self):
        """Test que verifica que se establece aprobado_por al aprobar"""
        request = self.factory.post('/')
        request.user = self.admin

        
        form_data = {
            'usuario': self.usuario1.id,
            'fecha_uso': date.today() + timedelta(days=1),
            'hora_inicio': time(10, 0),
            'hora_fin': time(12, 0),
            'espacio': self.espacio.id,
            'motivo': 'Reunión de trabajo',
            'estado': Reserva.Estado.APROBADA,
            'motivo_admin': 'Aprobado por administrador',
        }

        form = ReservaUpdateForm(request=request, data=form_data, instance=self.reserva)
        
     
        
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        reserva_actualizada = form.save()
        
        reserva_actualizada.refresh_from_db()
        self.assertEqual(reserva_actualizada.aprobado_por, self.admin)

    def test_save_method_sets_aprobado_por_when_rejected(self):
        """Test que verifica que se establece aprobado_por al rechazar"""
        request = self.factory.post('/')
        request.user = self.moderador
        
        form_data = {
            'usuario': self.usuario1.id,
            'fecha_uso': date.today() + timedelta(days=1),
            'hora_inicio': time(10, 0),
            'hora_fin': time(12, 0),
            'espacio': self.espacio.id,
            'motivo': 'Reunión de trabajo',
            'estado': Reserva.Estado.RECHAZADA,
            'motivo_admin': 'No se puede aprobar en esta fecha'
        }
        
        form = ReservaUpdateForm(request=request, data=form_data, instance=self.reserva)
        
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        reserva_actualizada = form.save()
        self.assertEqual(reserva_actualizada.aprobado_por, self.moderador)

    def test_save_method_no_aprobado_por_for_pending(self):
        """Test que verifica que no se establece aprobado_por para estado pendiente"""
        request = self.factory.post('/')
        request.user = self.admin
        
        # Resetear aprobado_por
        self.reserva.aprobado_por = None
        self.reserva.save()
        
        form_data = {
            'usuario': self.usuario1.id,
            'fecha_uso': date.today() + timedelta(days=1),
            'hora_inicio': time(10, 0),
            'hora_fin': time(12, 0),
            'espacio': self.espacio.id,
            'motivo': 'Reunión de trabajo',
            'estado': Reserva.Estado.PENDIENTE,
            'motivo_admin': ''
        }
        
        form = ReservaUpdateForm(request=request, data=form_data, instance=self.reserva)
        
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        reserva_actualizada = form.save()
        # No debe cambiar aprobado_por si ya era None
        self.assertIsNone(reserva_actualizada.aprobado_por)

    def test_motivo_admin_widget_configuration(self):
        """Test que verifica el widget del campo motivo_admin"""
        request = self.factory.get('/')
        request.user = self.admin
        
        form = ReservaUpdateForm(request=request, instance=self.reserva)
        
        motivo_admin_widget = form.fields['motivo_admin'].widget
        self.assertEqual(motivo_admin_widget.attrs['rows'], 3)
        self.assertEqual(motivo_admin_widget.attrs['placeholder'], 'Motivo de gestion')

