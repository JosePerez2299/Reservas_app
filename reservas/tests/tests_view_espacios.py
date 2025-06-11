
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from reservas.models import Ubicacion, Espacio, Reserva, Usuario


User = get_user_model()

class BaseEspacioTestCase(TestCase):

    def setUp(self):

        self.client = Client()
        
        self.ubicacion = Ubicacion.objects.create(nombre='Ubicación Test')
        
        # Crear grupos de usuarios
        self.admin_group = Group.objects.get_or_create(name=Usuario.GRUPOS.ADMINISTRADOR)[0]
        self.moderador_group = Group.objects.get_or_create(name=Usuario.GRUPOS.MODERADOR)[0]
        self.usuario_group = Group.objects.get_or_create(name=Usuario.GRUPOS.USUARIO)[0]
        
        # Crear usuarios con diferentes roles
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            ubicacion=self.ubicacion,
            piso=1
        )
        self.admin_user.groups.add(self.admin_group)
        self.admin_user.save()
        
        self.moderador_user = User.objects.create_user(
            username='moderador',
            email='moderador@test.com',
            password='testpass123',
            ubicacion=self.ubicacion,
            piso=1
        )
        self.moderador_user.groups.add(self.moderador_group)
        self.moderador_user.save()
        
        self.usuario_user = User.objects.create_user(
            username='usuario',
            email='usuario@test.com',
            password='testpass123',
            ubicacion=self.ubicacion,
            piso=1
        )
        self.usuario_user.groups.add(self.usuario_group)
        self.usuario_user.save()

        # Crear algunos objetos Espacio para tests de lista y update/delete
        self.espacios = []
        for i in range(35):
            espacio = Espacio.objects.create(
                nombre=f"Sala Base {i}",
                ubicacion=self.ubicacion,
                piso=(i % 3) + 1,
                capacidad=10 + i,
                tipo="Reunión",
                descripcion=f"Descripción {i}",
                disponible=(i % 2 == 0),
            )
            self.espacios.append(espacio)

class EspacioListViewTest(BaseEspacioTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('espacio')  
    
    def test_list_view_requires_login(self):
        """Test que la vista requiere autenticación"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302) 

    def test_list_view_requires_permission(self):
        """Test que la vista requiere permisos"""
        # Usuario no tiene permisos
        self.client.login(username='usuario', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403) 

        # Moderador no tiene permisos
        self.client.login(username='moderador', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403) 

        # Admin tiene permisos
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200) 
    
    def test_contain_ctx_espacios(self):
        """Test que valida la existencia del obj_list y los paginadores"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(self.url)  # página 1

        # 1) Verificamos status OK
        self.assertEqual(response.status_code, 200)

        # 2) Accedemos al paginator y page_obj
        paginator = response.context.get('paginator')
        page_obj = response.context.get('page_obj')
        self.assertIsNotNone(paginator, "El paginator no está en el contexto; verifica que la vista use paginate_by")
        self.assertIsNotNone(page_obj, "El page_obj no está en el contexto; verifica la configuración de paginación")

        # 3) Obtenemos la lista de objetos de la página actual
        object_list = response.context.get('object_list')
        self.assertIsNotNone(object_list, "La lista de objetos no se encuentra en el contexto")


    def test_admin_sees_all_espacios_with_pagination(self):
        """ Test que valida que el admin pueda ver todos los espacios """
        self.client.login(username='admin', password='testpass123')
        total = len(self.espacios)
        per_page = 10  # coincide con paginate_by de la vista
        num_pages = (total + per_page - 1) // per_page

        # 1) Validar acceder a una pagina no valida
        response= self.client.get(self.url + '?page=999')
        self.assertEqual(response.status_code, 302)


        # 2) Validar conteo de paginas con el total
        response= self.client.get(self.url)
        paginator = response.context.get('paginator')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(paginator.count, total)

  
        # 3) Contar pagina por pagina
        pages_responses = [ None for i in range(num_pages)]
        counter_items_pages = 0
        for i in range(num_pages):
            pages_responses[i]= self.client.get(self.url + '?page=' + str(i+1))

            response = pages_responses[i]

            # 1) Verificamos status OK
            self.assertEqual(response.status_code, 200)

            paginator = response.context.get('paginator')
            self.assertIsNotNone(paginator, "El paginator no está en el contexto; verifica que la vista use paginate_by")

            count_items = len(response.context.get('object_list'))
            counter_items_pages += count_items

        self.assertEqual(counter_items_pages, total) 


    def test_export_csv(self):
        # Si ListCrudMixin soporta export CSV con ?export=csv
        self.client.login(username='admin', password='testpass123')

        resp = self.client.get(self.url + '?export=csv')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv')
        contenido = resp.content.decode('utf-8')
        # Verificar encabezados esperados; ajusta según tu implementación de mixin
        cols = ['ID','Nombre','Tipo','Capacidad','Ubicación','Piso','Disponible']
        for col in cols:
            self.assertIn(col, contenido)
        # Líneas: 1 de cabecera + al menos 5 espacios creados
        lineas = contenido.strip().splitlines()
        self.assertGreaterEqual(len(lineas), 1 + len(self.espacios))

