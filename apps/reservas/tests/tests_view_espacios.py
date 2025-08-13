"""
Tests para las vistas de gestión de espacios.

Este módulo contiene tests para las operaciones CRUD de espacios:
- ListView: Listado paginado de espacios
- CreateView: Creación de nuevos espacios
- UpdateView: Actualización de espacios existentes
- DeleteView: Eliminación de espacios

Cada test verifica permisos, validaciones y funcionalidad específica.
"""
from datetime import date, time, timedelta

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from reservas.library.forms.espacios import EspacioCreateForm
from reservas.models import Ubicacion, Espacio, Reserva, Usuario

User = get_user_model()


class EspacioTestMixin:
    """
    Mixin que proporciona setup común para todos los tests de espacios.
    
    Crea usuarios con diferentes roles, ubicaciones y espacios de prueba
    para ser reutilizados en múltiples test cases.
    """
    
    def setUp(self):
        """Configuración inicial común para todos los tests."""
        super().setUp()
        self._setup_client()
        self._setup_ubicacion()
        self._setup_grupos_usuarios()
        self._setup_usuarios()
        self._setup_espacios_prueba()

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
            groups=[self.admin_group]
        )
        
        # Usuario moderador
        self.moderador_user = self._create_user(
            username='moderador',
            email='moderador@test.com',
            groups=[self.moderador_group]
        )
        
        # Usuario regular
        self.usuario_user = self._create_user(
            username='usuario',
            email='usuario@test.com',
            groups=[self.usuario_group]
        )
    
    def _create_user(self, username, email, groups=None):
        """
        Crea un usuario con los parámetros especificados.
        
        Args:
            username (str): Nombre de usuario
            email (str): Email del usuario
            groups (list): Lista de grupos a asignar
            
        Returns:
            User: Usuario creado
        """
        user = User.objects.create_user(
            username=username,
            email=email,
            password='testpass123',
            ubicacion=self.ubicacion,
            piso=1
        )
        
        if groups:
            user.groups.set(groups)
            
        return user
    
    def _setup_espacios_prueba(self):
        """Crea espacios de prueba para los tests de paginación y operaciones."""
        self.espacios = []
        
        for i in range(35):  # Suficientes para probar paginación
            espacio = Espacio.objects.create(
                nombre=f"Sala Test {i:02d}",
                ubicacion=self.ubicacion,
                piso=(i % 3) + 1,  # Pisos del 1 al 3
                capacidad=10 + (i % 20),  # Capacidades variadas
                tipo="laboratorio",
                descripcion=f"Sala de prueba número {i}",
                disponible=(i % 2 == 0),  # Alternar disponibilidad
            )
            self.espacios.append(espacio)

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


class EspacioListViewTest(EspacioTestMixin, TestCase):
    """Tests para la vista de listado de espacios."""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('espacio')
        self.per_page = 10  # Debe coincidir con paginate_by de la vista

    def test_requiere_autenticacion(self):
        """La vista debe requerir que el usuario esté autenticado."""
        self.assertRequiresLogin(self.url)

    def test_requiere_permisos_admin(self):
        """Solo los administradores pueden acceder a la lista de espacios."""
        self.assertRequiresPermission(self.url, allowed_users=[self.admin_user])

    def test_contexto_contiene_elementos_paginacion(self):
        """El contexto debe incluir paginator y page_obj para la paginación."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        
        # Verificar elementos de paginación
        self.assertIn('paginator', response.context,
                     "El contexto debe incluir 'paginator'")
        self.assertIn('page_obj', response.context,
                     "El contexto debe incluir 'page_obj'")
        self.assertIn('object_list', response.context,
                     "El contexto debe incluir 'object_list'")

    def test_paginacion_funciona_correctamente(self):
        """La paginación debe mostrar el número correcto de elementos por página."""
        self.client.login(username='admin', password='testpass123')
        
        total_espacios = len(self.espacios)
        expected_pages = (total_espacios + self.per_page - 1) // self.per_page
        
        # Test primera página
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        paginator = response.context['paginator']
        self.assertEqual(paginator.count, total_espacios,
                        "El paginator debe contar todos los espacios")
        self.assertEqual(paginator.num_pages, expected_pages,
                        f"Deberían haber {expected_pages} páginas")

    def test_pagina_invalida_redirecciona(self):
        """Acceder a una página inexistente debe redirigir."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(f"{self.url}?page=999")
        self.assertEqual(response.status_code, 302,
                        "Páginas inexistentes deben redirigir")

    def test_conteo_elementos_por_pagina(self):
        """Verificar que cada página contenga el número correcto de elementos."""
        self.client.login(username='admin', password='testpass123')
        
        total_espacios = len(self.espacios)
        num_pages = (total_espacios + self.per_page - 1) // self.per_page
        total_elementos_contados = 0
        
        for page_num in range(1, num_pages + 1):
            response = self.client.get(f"{self.url}?page={page_num}")
            self.assertEqual(response.status_code, 200)
            
            object_list = response.context['object_list']
            elementos_en_pagina = len(object_list)
            total_elementos_contados += elementos_en_pagina
            
            # La última página puede tener menos elementos
            if page_num < num_pages:
                self.assertEqual(elementos_en_pagina, self.per_page,
                               f"La página {page_num} debe tener {self.per_page} elementos")
        
        self.assertEqual(total_elementos_contados, total_espacios,
                        "El total de elementos en todas las páginas debe coincidir")

    def test_exportacion_csv(self):
        """Los administradores pueden exportar la lista en formato CSV."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(f"{self.url}?export=csv")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        contenido = response.content.decode('utf-8')
        
        # Verificar headers esperados
        headers_esperados = ['ID', 'Nombre', 'Tipo', 'Capacidad', 'Ubicación', 'Piso', 'Disponible']
        for header in headers_esperados:
            self.assertIn(header, contenido, f"Header '{header}' debe estar presente")
        
        # Verificar que incluye datos de los espacios
        lineas = contenido.strip().splitlines()
        expected_lines = 1 + len(self.espacios)  # Header + espacios
        self.assertEqual(len(lineas), expected_lines,
                        f"Debe haber {expected_lines} líneas en el CSV")


class EspacioCreateViewTest(EspacioTestMixin, TestCase):
    """Tests para la vista de creación de espacios."""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('espacio_create')

    def test_requiere_autenticacion(self):
        """La vista debe requerir autenticación."""
        self.assertRequiresLogin(self.url)

    def test_requiere_permisos_admin(self):
        """Solo administradores pueden crear espacios."""
        self.assertRequiresPermission(self.url, allowed_users=[self.admin_user])

    def test_get_muestra_formulario_correcto(self):
        """GET debe mostrar el formulario de creación con todos los campos."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        # Verificar que el formulario está en el contexto
        self.assertIn('form', response.context)
        form = response.context['form']
        
        # Verificar tipo de formulario
        self.assertIsInstance(form, EspacioCreateForm,
                             "Debe usar EspacioCreateForm")
        
        # Verificar campos requeridos
        campos_esperados = {
            'nombre', 'ubicacion', 'piso', 'capacidad', 
            'tipo', 'descripcion', 'disponible'
        }
        self.assertEqual(set(form.fields.keys()), campos_esperados,
                        "El formulario debe tener todos los campos esperados")

    def test_post_datos_validos_crea_espacio(self):
        """POST con datos válidos debe crear un nuevo espacio."""
        self.client.login(username='admin', password='testpass123')
        
        espacios_iniciales = Espacio.objects.count()
        
        datos_validos = {
            'nombre': 'Sala Nueva',
            'ubicacion': self.ubicacion.pk,
            'piso': 2,
            'capacidad': 25,
            'tipo': 'laboratorio',
            'descripcion': 'Sala creada en test',
            'disponible': True,
        }
        
        response = self.client.post(self.url, datos_validos)
        
        # Debe redirigir después de crear exitosamente
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó el espacio
        self.assertEqual(Espacio.objects.count(), espacios_iniciales + 1,
                        "Debe haberse creado un nuevo espacio")
        
        # Verificar datos del espacio creado
        espacio_creado = Espacio.objects.get(nombre='Sala Nueva')
        self.assertEqual(espacio_creado.ubicacion, self.ubicacion)
        self.assertEqual(espacio_creado.capacidad, 25)
        self.assertEqual(espacio_creado.tipo, 'laboratorio')

    def test_post_datos_invalidos_muestra_errores(self):
        """POST con datos inválidos debe mostrar errores y no crear espacio."""
        self.client.login(username='admin', password='testpass123')
        
        espacios_iniciales = Espacio.objects.count()
        
        datos_invalidos = {
            'nombre': '',           # Requerido
            'ubicacion': '',        # Inválido
            'piso': -1,            # Fuera de rango
            'capacidad': 0,        # Debe ser > 0
            'tipo': '',            # Requerido
            'descripcion': '',
            'disponible': True,
        }
        
        response = self.client.post(self.url, datos_invalidos)
        
        # No debe redirigir, debe mostrar errores
        self.assertEqual(response.status_code, 200,
                        "Debe quedarse en la misma página para mostrar errores")
        
        # Verificar que hay errores en el formulario
        form = response.context.get('form')
        self.assertIsNotNone(form, "Debe haber un formulario en el contexto")
        self.assertTrue(form.errors, "El formulario debe tener errores")
        
        # Verificar errores en campos específicos
        campos_con_error = ['nombre', 'ubicacion', 'piso', 'capacidad', 'tipo']
        for campo in campos_con_error:
            self.assertIn(campo, form.errors,
                         f"Campo '{campo}' debe tener error")
        
        # No debe haberse creado ningún espacio
        self.assertEqual(Espacio.objects.count(), espacios_iniciales,
                        "No debe haberse creado ningún espacio con datos inválidos")


class EspacioUpdateViewTest(EspacioTestMixin, TestCase):
    """Tests para la vista de actualización de espacios."""
    
    def setUp(self):
        super().setUp()
        self.espacio_test = self.espacios[0]  # Usar el primer espacio de prueba
        self.url = reverse('espacio_edit', args=[self.espacio_test.pk])

    def test_requiere_autenticacion(self):
        """La vista debe requerir autenticación."""
        self.assertRequiresLogin(self.url)

    def test_requiere_permisos_admin(self):
        """Solo administradores pueden editar espacios."""
        self.assertRequiresPermission(self.url, allowed_users=[self.admin_user])

    def test_get_muestra_datos_actuales(self):
        """GET debe mostrar el formulario pre-llenado con los datos actuales."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        form = response.context['form']
        
        # Verificar que los datos actuales están en el formulario
        datos_esperados = {
            'nombre': self.espacio_test.nombre,
            'ubicacion': self.espacio_test.ubicacion.pk,
            'piso': self.espacio_test.piso,
            'capacidad': self.espacio_test.capacidad,
            'tipo': self.espacio_test.tipo,
            'descripcion': self.espacio_test.descripcion,
            'disponible': self.espacio_test.disponible,
        }
        
        for campo, valor_esperado in datos_esperados.items():
            valor_actual = form.initial.get(campo)
            self.assertEqual(valor_actual, valor_esperado,
                           f"Campo '{campo}' debe tener el valor actual")

    def test_post_actualiza_espacio_correctamente(self):
        """POST con datos válidos debe actualizar el espacio."""
        self.client.login(username='admin', password='testpass123')
        
        datos_actualizados = {
            'nombre': 'Sala Actualizada',
            'ubicacion': self.ubicacion.pk,
            'piso': self.espacio_test.piso,
            'capacidad': self.espacio_test.capacidad,
            'tipo': self.espacio_test.tipo,
            'descripcion': 'Descripción actualizada',
            'disponible': self.espacio_test.disponible,
        }
        
        response = self.client.post(self.url, datos_actualizados)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que los cambios se guardaron
        self.espacio_test.refresh_from_db()
        self.assertEqual(self.espacio_test.nombre, 'Sala Actualizada')
        self.assertEqual(self.espacio_test.descripcion, 'Descripción actualizada')

    def test_cambiar_disponible_false_rechaza_reservas_futuras(self):
        """Cambiar disponible a False debe rechazar reservas futuras pendientes."""
        self.client.login(username='admin', password='testpass123')
        
        # Asegurar que el espacio esté disponible inicialmente
        self.espacio_test.disponible = True
        self.espacio_test.save()
        
        # Crear una reserva futura pendiente
        fecha_futura = date.today() + timedelta(days=2)
        reserva = Reserva.objects.create(
            espacio=self.espacio_test,
            usuario=self.usuario_user,
            fecha_uso=fecha_futura,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado=Reserva.Estado.PENDIENTE,
        )
        
        # Cambiar espacio a no disponible
        datos_actualizacion = {
            'nombre': self.espacio_test.nombre,
            'ubicacion': self.ubicacion.pk,
            'piso': self.espacio_test.piso,
            'capacidad': self.espacio_test.capacidad,
            'tipo': self.espacio_test.tipo,
            'descripcion': self.espacio_test.descripcion,
            'disponible': False,  # Cambiar a no disponible
        }
        
        response = self.client.post(self.url, datos_actualizacion)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la reserva fue rechazada
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, Reserva.Estado.RECHAZADA,
                        "La reserva debe ser rechazada")
        self.assertEqual(reserva.aprobado_por, self.admin_user,
                        "El admin debe ser quien rechazó")
        self.assertEqual(reserva.motivo_admin, 'El espacio no se encuentra disponible',
                        "Debe tener el motivo correcto")


class EspacioDeleteViewTest(EspacioTestMixin, TestCase):
    """Tests para la vista de eliminación de espacios."""
    
    def setUp(self):
        super().setUp()
        # Crear un espacio específico para eliminar
        self.espacio_a_eliminar = Espacio.objects.create(
            nombre='Sala para Eliminar',
            ubicacion=self.ubicacion,
            piso=1,
            capacidad=10,
            tipo='Aula',
            descripcion='Espacio temporal para test de eliminación',
            disponible=True,
        )
        self.url = reverse('espacio_delete', args=[self.espacio_a_eliminar.pk])

    def test_requiere_autenticacion(self):
        """La vista debe requerir autenticación."""
        self.assertRequiresLogin(self.url)

    def test_requiere_permisos_admin(self):
        """Solo administradores pueden eliminar espacios."""
        self.assertRequiresPermission(self.url, allowed_users=[self.admin_user])

    def test_get_muestra_confirmacion(self):
        """GET debe mostrar página de confirmación de eliminación."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200,
                        "Debe mostrar página de confirmación")

    def test_post_elimina_espacio(self):
        """POST debe eliminar el espacio correctamente."""
        self.client.login(username='admin', password='testpass123')
        
        espacios_iniciales = Espacio.objects.count()
        espacio_pk = self.espacio_a_eliminar.pk
        
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302,
                        "Debe redirigir después de eliminar")
        
        # Verificar que el espacio fue eliminado
        self.assertEqual(Espacio.objects.count(), espacios_iniciales - 1,
                        "Debe haberse eliminado un espacio")
        self.assertFalse(Espacio.objects.filter(pk=espacio_pk).exists(),
                        "El espacio específico debe haber sido eliminado")

    def test_eliminacion_con_reservas_asociadas(self):
        """Eliminar espacio debe manejar correctamente reservas asociadas."""
        self.client.login(username='admin', password='testpass123')
        
        # Crear una reserva asociada al espacio
        reserva = Reserva.objects.create(
            usuario=self.usuario_user,
            espacio=self.espacio_a_eliminar,
            fecha_uso=date.today() + timedelta(days=1),
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
            motivo='Reunión importante',
            estado=Reserva.Estado.PENDIENTE
        )
        
        espacio_pk = self.espacio_a_eliminar.pk
        reserva_pk = reserva.pk
        
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que tanto el espacio como la reserva fueron eliminados
        self.assertFalse(Espacio.objects.filter(pk=espacio_pk).exists(),
                        "El espacio debe haber sido eliminado")
        self.assertFalse(Reserva.objects.filter(pk=reserva_pk).exists(),
                        "La reserva asociada debe haber sido eliminada (CASCADE)")