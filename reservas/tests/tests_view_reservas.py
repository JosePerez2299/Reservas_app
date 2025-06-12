"""
Tests para las vistas de gestión de reservas.

Este módulo contiene tests para las operaciones CRUD de reservas:
- ListView: Listado paginado de reservas con filtros
- CreateView: Creación de nuevas reservas
- UpdateView: Actualización de reservas existentes
- DetailView: Visualización de detalles de reservas
- DeleteView: Eliminación de reservas existentes

Cada test verifica permisos, validaciones y funcionalidad específica.
"""
from datetime import date, time, timedelta

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from reservas.library.forms.reservas import ReservaCreateForm, ReservaUpdateForm
from reservas.models import Ubicacion, Espacio, Reserva, Usuario

User = get_user_model()


class ReservaTestMixin:
    """
    Mixin que proporciona setup común para todos los tests de reservas.
    
    Crea usuarios con diferentes roles, ubicaciones, espacios y reservas de prueba
    para ser reutilizados en múltiples test cases.
    """
    
    def setUp(self):
        """Configuración inicial común para todos los tests."""
        super().setUp()
        self._setup_client()
        self._setup_ubicacion()
        self._setup_grupos_usuarios()
        self._setup_usuarios()
        self._setup_espacios()
        self._setup_reservas_prueba()

    def _setup_client(self):
        """Inicializa el cliente de test."""
        self.client = Client()
    
    def _setup_ubicacion(self):
        """Crea una ubicación de prueba."""
        self.ubicacion = Ubicacion.objects.create(nombre='Ubicación Test')
    
    def _setup_grupos_usuarios(self):
        """Crea los grupos de usuarios necesarios."""
        self.admin_group, _ = Group.objects.get_or_create(
            name=Usuario.GRUPOS.ADMINISTRADOR
        )
        self.moderador_group, _ = Group.objects.get_or_create(
            name=Usuario.GRUPOS.MODERADOR
        )
        self.usuario_group, _ = Group.objects.get_or_create(
            name=Usuario.GRUPOS.USUARIO
        )
    
    def _setup_usuarios(self):
        """Crea usuarios con diferentes roles para los tests."""
        # Usuario administrador
        self.admin_user = self._create_user(
            username='admin',
            email='admin@test.com',
            groups=[self.admin_group],
            ubicacion=self.ubicacion,
            piso=1
        )
        
        # Usuario moderador
        self.moderador_user = self._create_user(
            username='moderador',
            email='moderador@test.com',
            groups=[self.moderador_group],
            ubicacion=self.ubicacion,
            piso=1
        )
        
        # Usuario regular
        self.usuario_user = self._create_user(
            username='usuario',
            email='usuario@test.com',
            groups=[self.usuario_group],
            ubicacion=self.ubicacion,
            piso=1
        )
    
    def _create_user(self, username, email, groups=None, **extra_fields):
        """
        Crea un usuario con los parámetros especificados.
        
        Args:
            username (str): Nombre de usuario
            email (str): Email del usuario
            groups (list): Lista de grupos a asignar
            **extra_fields: Campos adicionales del modelo Usuario
            
        Returns:
            User: Usuario creado
        """
        user = User.objects.create_user(
            username=username,
            email=email,
            password='testpass123',
            **extra_fields
        )
        
        if groups:
            user.groups.set(groups)
            
        return user
    
    def _setup_espacios(self):
        """Crea espacios de prueba para los tests de reservas."""
        self.espacios = []
        
        for i in range(5):
            espacio = Espacio.objects.create(
                nombre=f"Sala Test {i}",
                ubicacion=self.ubicacion,
                piso=(i % 3) + 1,  # Pisos del 1 al 3
                capacidad=10 + (i * 5),
                tipo="sala",
                descripcion=f"Sala de prueba {i}",
                disponible=True,
            )
            self.espacios.append(espacio)
    
    def _setup_reservas_prueba(self):
        """Crea reservas de prueba."""
        self.reservas = []
        now = timezone.now()
        
        # Crear algunas reservas pasadas
        for i in range(10):
            reserva = Reserva.objects.create(
                usuario=self.usuario_user,
                espacio=self.espacios[i % len(self.espacios)],
                fecha_creacion=now - timedelta(days=10-i),
                fecha_uso=now.date() - timedelta(days=10-i),
                hora_inicio=time(9, 0),
                hora_fin=time(10, 0),
                motivo=f"Reunión {i}",
                estado=Reserva.ESTADOS.APROBADA if i % 2 == 0 else Reserva.ESTADOS.RECHAZADA,
                aprobado_por=self.admin_user if i % 2 == 0 else None
            )
            self.reservas.append(reserva)
        
        # Crear algunas reservas futuras
        for i in range(5):
            reserva = Reserva.objects.create(
                usuario=self.usuario_user,
                espacio=self.espacios[i % len(self.espacios)],
                fecha_creacion=now,
                fecha_uso=now.date() + timedelta(days=i+1),
                hora_inicio=time(14, 0),
                hora_fin=time(16, 0),
                motivo=f"Evento futuro {i}",
                estado=Reserva.ESTADOS.PENDIENTE,
                aprobado_por=None
            )
            self.reservas.append(reserva)
    
    # Métodos helper para tests comunes
    def assertRequiresLogin(self, url):
        """Verifica que la URL requiere autenticación."""
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302, 
                        "La vista debería redirigir usuarios no autenticados")

    def assertRequiresPermission(self, url, allowed_users=None):
        """
        Verifica que la URL requiere permisos específicos.
        
        Args:
            url (str): URL a testear
            allowed_users (list): Lista de usuarios que deberían tener acceso
        """
        allowed_users = allowed_users or [self.admin_user]
        
        # Test usuarios sin permisos
        for user in [self.usuario_user, self.moderador_user]:
            if user not in allowed_users:
                self.client.login(username=user.username, password='testpass123')
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403,
                               f"{user.username} no debería tener acceso")
        
        # Test usuarios con permisos
        for user in allowed_users:
            self.client.login(username=user.username, password='testpass123')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200,
                           f"{user.username} debería tener acceso")


class ReservaListViewTest(ReservaTestMixin, TestCase):
    """Tests para la vista de listado de reservas."""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('reserva')
        self.per_page = 10  # Debe coincidir con paginate_by de la vista

    def test_requiere_autenticacion(self):
        """La vista debe requerir que el usuario esté autenticado."""
        self.assertRequiresLogin(self.url)

    def test_permisos_por_rol(self):
        """Verifica los permisos de acceso según el rol del usuario."""
        # Admin puede ver todas las reservas
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 15)  # Todas las reservas
        
        # Moderador solo ve sus reservas o las de su ubicación/piso
        self.client.login(username='moderador', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        # Usuario solo ve sus propias reservas
        self.client.login(username='usuario', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 15)  # Todas son del usuario

    def test_filtros_funcionan_correctamente(self):
        """Los filtros deben filtrar correctamente las reservas."""
        self.client.login(username='admin', password='testpass123')
        
        # Filtrar por estado
        response = self.client.get(self.url, {'estado': 'PENDIENTE'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(r.estado == 'PENDIENTE' for r in response.context['object_list']))
        
        # Filtrar por fecha
        hoy = date.today()
        response = self.client.get(self.url, {
            'fecha_uso_after': hoy.isoformat(),
            'fecha_uso_before': (hoy + timedelta(days=7)).isoformat()
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(hoy <= r.fecha_uso <= hoy + timedelta(days=7) 
                          for r in response.context['object_list']))


class ReservaCreateViewTest(ReservaTestMixin, TestCase):
    """Tests para la vista de creación de reservas."""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('reserva_create')
    
    def test_requiere_autenticacion(self):
        """La vista debe requerir que el usuario esté autenticado."""
        self.assertRequiresLogin(self.url)
    
    def test_permisos_creacion(self):
        """Cualquier usuario autenticado puede crear reservas."""
        for user in [self.usuario_user, self.moderador_user, self.admin_user]:
            self.client.login(username=user.username, password='testpass123')
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200, 
                          f"{user.username} debería poder acceder")
    
    def test_creacion_reserva_valida(self):
        """Se puede crear una reserva con datos válidos."""
        self.client.login(username='usuario', password='testpass123')
        
        tomorrow = (timezone.now() + timedelta(days=1)).date()
        data = {
            'espacio': self.espacios[0].id,
            'fecha_uso': tomorrow.isoformat(),
            'hora_inicio': '09:00:00',
            'hora_fin': '10:00:00',
            'motivo': 'Reunión de prueba',
            'estado': 'PENDIENTE',
        }
        
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Reserva.objects.filter(motivo='Reunión de prueba').exists())
    
    def test_validacion_solapa_reserva(self):
        """No se puede reservar un espacio que ya está reservado."""
        self.client.login(username='usuario', password='testpass123')
        
        # Crear una reserva existente
        fecha = (timezone.now() + timedelta(days=1)).date()
        Reserva.objects.create(
            usuario=self.usuario_user,
            espacio=self.espacios[0],
            fecha_uso=fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            motivo='Reserva existente',
            estado='APROBADA'
        )
        
        # Intentar crear una reserva que se solapa
        data = {
            'espacio': self.espacios[0].id,
            'fecha_uso': fecha.isoformat(),
            'hora_inicio': '09:30:00',
            'hora_fin': '10:30:00',
            'motivo': 'Reunión que se solapa',
            'estado': 'PENDIENTE',
        }
        
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)  # Debe haber errores de validación


class ReservaUpdateViewTest(ReservaTestMixin, TestCase):
    """Tests para la vista de actualización de reservas."""
    
    def setUp(self):
        super().setUp()
        self.reserva = self.reservas[0]  # Una reserva existente
        self.url = reverse('reserva_edit', kwargs={'pk': self.reserva.pk})
    
    def test_requiere_autenticacion(self):
        """La vista debe requerir que el usuario esté autenticado."""
        self.assertRequiresLogin(self.url)
    
    def test_permisos_edicion(self):
        """Solo el dueño de la reserva o un admin pueden editarla."""
        # Usuario que no es dueño
        otro_usuario = self._create_user(
            username='otro', 
            email='otro@test.com',
            groups=[self.usuario_group],
            ubicacion=self.ubicacion,
            piso=1
        )
        
        self.client.login(username='otro', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # Prohibido
        
        # Dueño puede editar
        self.client.login(username='usuario', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        # Admin puede editar
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_actualizacion_reserva(self):
        """Se puede actualizar una reserva existente."""
        self.client.login(username='usuario', password='testpass123')
        
        data = {
            'espacio': self.reserva.espacio.id,
            'fecha_uso': self.reserva.fecha_uso.isoformat(),
            'hora_inicio': self.reserva.hora_inicio.strftime('%H:%M:%S'),
            'hora_fin': (time.fromisoformat(self.reserva.hora_fin.strftime('%H:%M:%S')) + timedelta(hours=1)).strftime('%H:%M:%S'),
            'motivo': 'Motivo actualizado',
            'estado': self.reserva.estado,
        }
        
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.motivo, 'Motivo actualizado')


class ReservaDetailViewTest(ReservaTestMixin, TestCase):
    """Tests para la vista de detalles de reserva."""
    
    def setUp(self):
        super().setUp()
        self.reserva = self.reservas[0]
        self.url = reverse('reserva_view', kwargs={'pk': self.reserva.pk})
    
    def test_requiere_autenticacion(self):
        """La vista debe requerir que el usuario esté autenticado."""
        self.assertRequiresLogin(self.url)
    
    def test_permisos_visualizacion(self):
        """Solo el dueño, admin o moderador pueden ver los detalles."""
        # Usuario que no es dueño
        otro_usuario = self._create_user(
            username='otro', 
            email='otro@test.com',
            groups=[self.usuario_group],
            ubicacion=self.ubicacion,
            piso=1
        )
        
        self.client.login(username='otro', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # Prohibido
        
        # Dueño puede ver
        self.client.login(username='usuario', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        # Admin puede ver
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        # Moderador puede ver
        self.client.login(username='moderador', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class ReservaDeleteViewTest(ReservaTestMixin, TestCase):
    """Tests para la vista de eliminación de reservas."""
    
    def setUp(self):
        super().setUp()
        self.reserva = self.reservas[0]
        self.url = reverse('reserva_delete', kwargs={'pk': self.reserva.pk})
    
    def test_requiere_autenticacion(self):
        """La vista debe requerir que el usuario esté autenticado."""
        self.assertRequiresLogin(self.url)
    
    def test_permisos_eliminacion(self):
        """Solo el dueño o un admin pueden eliminar la reserva."""
        # Usuario que no es dueño
        otro_usuario = self._create_user(
            username='otro', 
            email='otro@test.com',
            groups=[self.usuario_group],
            ubicacion=self.ubicacion,
            piso=1
        )
        
        self.client.login(username='otro', password='testpass123')
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 403)  # Prohibido
        
        # Dueño puede eliminar
        self.client.login(username='usuario', password='testpass123')
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Reserva.objects.filter(pk=self.reserva.pk).exists())
        
        # Recrear la reserva eliminada
        self.reserva.pk = None
        self.reserva.save()
        
        # Admin puede eliminar
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(
            reverse('reserva_delete', kwargs={'pk': self.reserva.pk}), 
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Reserva.objects.filter(pk=self.reserva.pk).exists())
    
    def test_eliminacion_por_post(self):
        """La eliminación solo debe funcionar con POST."""
        self.client.login(username='usuario', password='testpass123')
        
        # GET no debería eliminar
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)  # Muestra confirmación
        self.assertTrue(Reserva.objects.filter(pk=self.reserva.pk).exists())
        
        # POST sí debe eliminar
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Reserva.objects.filter(pk=self.reserva.pk).exists())
