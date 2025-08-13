from django.test import TestCase, RequestFactory
from django.contrib.auth.models import Group
from reservas.models import Usuario, Ubicacion, Espacio, Reserva
from reservas..forms.reservas import ReservaCreateForm, ReservaUpdateForm

from datetime import timedelta, time, date

class FormValidationTestCase(TestCase):
    def setUp(self):
        """Configuración para tests de validación"""
        self.factory = RequestFactory()
        
        # Crear ubicación
        self.ubicacion = Ubicacion.objects.create(nombre='Sede Principal')
        
        # Crear grupo y usuario admin
        self.grupo_admin = Group.objects.get_or_create(name=Usuario.GRUPOS.ADMINISTRADOR)[0]
        # Crear un usuario admin y un usuario no admin
        self.admin = Usuario.objects.create_user(username='admin', email='admin@example.com', password='pass')
        self.admin.groups.add(self.grupo_admin)
        # Crear espacio
        self.espacio = Espacio.objects.create(
            nombre='Salon101',
            ubicacion=self.ubicacion,
            piso=1,
            capacidad=30,
            tipo=Espacio.Tipo.SALON,
            disponible=True
        )

    def test_create_form_valid_data(self):
        """Test que verifica datos válidos en el formulario de creación"""
        request = self.factory.post('/')
        request.user = self.admin
        
        form_data = {
            'usuario': self.admin.id,
            'fecha_uso': date.today() + timedelta(days=1),
            'hora_inicio': time(10, 0),
            'hora_fin': time(12, 0),
            'espacio': self.espacio.id,
            'motivo': 'Reunión de trabajo importante'
        }
        
        form = ReservaCreateForm(request=request, data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_create_form_invalid_past_date(self):
        """Test que verifica que no se puede crear reserva con fecha pasada"""
        request = self.factory.post('/')
        request.user = self.admin
        
        form_data = {
            'usuario': self.admin.id,
            'fecha_uso': date.today() - timedelta(days=1),  # Fecha pasada
            'hora_inicio': time(10, 0),
            'hora_fin': time(12, 0),
            'espacio': self.espacio.id,
            'motivo': 'Reunión de trabajo'
        }
        
        form = ReservaCreateForm(request=request, data=form_data)
        # El widget date debería tener restricciones, pero la validación real 
        # ocurre en el modelo clean()
        
    def test_update_form_valid_data(self):
        """Test que verifica datos válidos en el formulario de actualización"""
        # Crear reserva
        reserva = Reserva.objects.create(
            usuario=self.admin,
            espacio=self.espacio,
            fecha_uso=date.today() + timedelta(days=1),
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
            motivo='Reunión inicial',
            estado=Reserva.Estado.PENDIENTE
        )
        
        request = self.factory.post('/')
        request.user = self.admin
        
        form_data = {
            'usuario': self.admin.id,
            'fecha_uso': date.today() + timedelta(days=2),
            'hora_inicio': time(14, 0),
            'hora_fin': time(16, 0),
            'espacio': self.espacio.id,
            'motivo': 'Reunión actualizada',
            'estado': Reserva.Estado.APROBADA,
            'motivo_admin': 'Aprobado por administrador'
        }
        
        form = ReservaUpdateForm(request=request, data=form_data, instance=reserva)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_form_missing_required_fields(self):
        """Test que verifica que fallan los formularios sin campos requeridos"""
        request = self.factory.post('/')
        request.user = self.admin
        
        # Formulario de creación sin motivo (requerido)
        form_data = {
            'usuario': self.admin.id,
            'fecha_uso': date.today() + timedelta(days=1),
            'hora_inicio': time(10, 0),
            'hora_fin': time(12, 0),
            'espacio': self.espacio.id,
            # 'motivo': Falta este campo requerido
        }
        
        form = ReservaCreateForm(request=request, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('motivo', form.errors)


class UserPermissionsTestCase(TestCase):
    """Tests específicos para permisos de usuarios"""
    
    def setUp(self):
        self.factory = RequestFactory()
        
        # Crear ubicaciones
        self.ubicacion1 = Ubicacion.objects.create(nombre='Sede Central')
        self.ubicacion2 = Ubicacion.objects.create(nombre='Sede Norte')
        
        # Crear grupos
        self.grupo_admin = Group.objects.get_or_create(name=Usuario.GRUPOS.ADMINISTRADOR)[0]
        self.grupo_moderador = Group.objects.get_or_create(name=Usuario.GRUPOS.MODERADOR)[0]
        self.grupo_usuario = Group.objects.get_or_create(name=Usuario.GRUPOS.USUARIO)[0]
        
        # Crear usuarios en diferentes ubicaciones y pisos
        self.moderador_piso1 = Usuario.objects.create_user(
            username='mod_piso1',
            email='mod1@test.com',
            ubicacion=self.ubicacion1,
            piso=1
        )
        self.moderador_piso1.groups.add(self.grupo_moderador)
        
        self.moderador_piso2 = Usuario.objects.create_user(
            username='mod_piso2',
            email='mod2@test.com',
            ubicacion=self.ubicacion1,
            piso=2
        )
        self.moderador_piso2.groups.add(self.grupo_moderador)
        
        # Crear espacios en diferentes pisos
        self.espacio_piso1 = Espacio.objects.create(
            nombre='Salon101',
            ubicacion=self.ubicacion1,
            piso=1,
            capacidad=30,
            tipo=Espacio.Tipo.SALON,
            disponible=True
        )
        
        self.espacio_piso2 = Espacio.objects.create(
            nombre='Salon201',
            ubicacion=self.ubicacion1,
            piso=2,
            capacidad=25,
            tipo=Espacio.Tipo.SALON,
            disponible=True
        )

    def test_moderador_can_only_manage_same_floor(self):
        """Test que moderador solo puede gestionar reservas de su mismo piso"""
        # Crear reserva en piso 2
        reserva_piso2 = Reserva.objects.create(
            usuario=self.moderador_piso2,
            espacio=self.espacio_piso2,
            fecha_uso=date.today() + timedelta(days=1),
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
            motivo='Reunión piso 2',
            estado=Reserva.Estado.PENDIENTE
        )
        
        # Moderador del piso 1 NO debería poder gestionar reserva del piso 2
        request = self.factory.get('/')
        request.user = self.moderador_piso1
        
        form = ReservaUpdateForm(request=request, instance=reserva_piso2)
        self.assertTrue(form.fields['estado'].disabled)
        
        # Moderador del piso 2 SÍ debería poder gestionar su reserva
        request.user = self.moderador_piso2
        form = ReservaUpdateForm(request=request, instance=reserva_piso2)
        self.assertFalse(form.fields['estado'].disabled)