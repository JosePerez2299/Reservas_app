from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta
from reservas.models import Ubicacion, Espacio, Reserva, Usuario

User = get_user_model()

class BaseEspacioTestCase:
    def setup_espacios(self):

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
                tipo="laboratorio",
                descripcion=f"Descripción {i}",
                disponible=(i % 2 == 0),
            )
            self.espacios.append(espacio)

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
    

class EspacioListViewTest(TestCase, BaseEspacioTestCase):
    def setUp(self):
        super().setup_espacios()
        self.url = reverse('espacio')  
   
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
            object_list = response.context.get('object_list')
            paginator = response.context.get('paginator')
            self.assertIsNotNone(paginator, "El paginator no está en el contexto; verifica que la vista use paginate_by")

            count_items = len(object_list)
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


class EspacioCreateViewTest(TestCase, BaseEspacioTestCase):
    def setUp(self):
        super().setup_espacios()
        self.url = reverse('espacio_create')  

    def test_get_create_view_muestra_form(self):
        self.client.login(username='admin', password='testpass123')

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        
        form = resp.context['form']
        
        # Verificar que el formulario es una instancia de EspacioCreateForm
        from reservas.library.forms.espacios import EspacioCreateForm
        self.assertIsInstance(form, EspacioCreateForm)
        
        # Verificar que todos los campos requeridos están presentes
        expected_fields = [
            'nombre', 'ubicacion', 'piso', 'capacidad', 
            'tipo', 'descripcion', 'disponible'
        ]
        self.assertCountEqual(form.fields.keys(), expected_fields)
        
        # Verificar que todos los campos requeridos están presentes
        self.assertIsNotNone(form.fields['nombre'])
        self.assertIsNotNone(form.fields['ubicacion'])
        self.assertIsNotNone(form.fields['piso'])
        self.assertIsNotNone(form.fields['capacidad'])
        self.assertIsNotNone(form.fields['tipo'])
        self.assertIsNotNone(form.fields['descripcion'])
        self.assertTrue(form.fields['disponible'])
        

    def test_post_create_valid(self):
        self.client.login(username='admin', password='testpass123')

        datos = {
            'nombre': 'Sala desde el create',
            'ubicacion': self.ubicacion.pk,
            'piso': 2,
            'capacidad': 25,
            'tipo': 'laboratorio',
            'descripcion': 'Nueva Sala',
            'disponible': True,
        }
        resp = self.client.post(self.url, datos)

        self.assertEqual(resp.status_code, 302)
        # Verificar que existe en BD
        existe = Espacio.objects.filter(nombre='Sala desde el create', ubicacion=self.ubicacion).exists()
        self.assertTrue(existe)

    def test_post_create_invalid(self):
        self.client.login(username='admin', password='testpass123')

        logged = self.client.login(username='admin', password='testpass123')
        self.assertTrue(logged, "Falla login en test: revisa credenciales")
        
        datos_invalidos = {
            'nombre': '',        # nombre requerido
            'ubicacion': '',     # inválido
            'piso': -1,          # fuera de rango si hay validación
            'capacidad': 0,      # debe ser > 0
            'tipo': '',          # requerido
            'descripcion': '',   # asumimos requerido o puede permitirse vacío, pero incluimos
            'disponible': True,
        }
        # Contar cuántos espacios hay antes
        inicial = Espacio.objects.count()
        
        resp = self.client.post(self.url, datos_invalidos)
        # No redirige, status 200 con el form mostrando errores
        self.assertEqual(resp.status_code, 200)
        
        # Debe haber formulario en contexto
        form = resp.context.get('form')
        self.assertIsNotNone(form, "No se encontró 'form' en el contexto")
        
        # El form debe tener errores
        self.assertTrue(form.errors, "Se esperaba que el form tuviera errores pero está limpio")
        
        # Verificar campos específicos tienen error
        for campo in ['nombre', 'ubicacion', 'piso', 'capacidad', 'tipo']:
            self.assertIn(campo, form.errors, f"Se esperaba error en el campo '{campo}'")
        
        # Opcional: verificar que el queryset no cambió
        self.assertEqual(Espacio.objects.count(), inicial, "Se creó un Espacio inválido cuando no debía")

class EspacioUpdateViewTest(TestCase, BaseEspacioTestCase):
    def setUp(self):
        super().setup_espacios()
        self.espacio = self.espacios[0]
        self.url = reverse('espacio_edit', args=[self.espacio.pk])

    def test_get_update_view_obtain_data(self):
        self.client.login(username='admin', password='testpass123')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        form = resp.context['form']
        self.assertEqual(form.initial.get('nombre'), self.espacio.nombre)
        self.assertEqual(form.initial.get('ubicacion'), self.espacio.ubicacion.pk)
        self.assertEqual(form.initial.get('piso'), self.espacio.piso)
        self.assertEqual(form.initial.get('capacidad'), self.espacio.capacidad)
        self.assertEqual(form.initial.get('tipo'), self.espacio.tipo)
        self.assertEqual(form.initial.get('descripcion'), self.espacio.descripcion)
        self.assertEqual(form.initial.get('disponible'), self.espacio.disponible)

    def test_post_update_valido_modifica_objeto(self):
        self.client.login(username='admin', password='testpass123')
        nuevos_datos = {
            'nombre': 'Sala Modificada',
            'ubicacion': self.ubicacion.pk,
            'piso': self.espacio.piso,
            'capacidad': self.espacio.capacidad,
            'tipo': self.espacio.tipo,
            'descripcion': 'Descripción modificada',
            'disponible': self.espacio.disponible,
        }   
        resp = self.client.post(self.url, nuevos_datos)
        self.assertEqual(resp.status_code, 302)
        self.espacio.refresh_from_db()

        self.assertEqual(self.espacio.nombre, 'Sala Modificada')
        self.assertEqual(self.espacio.descripcion, 'Descripción modificada')

    def test_post_update_cambio_disponible_false_rechaza_reservas(self):
        logged = self.client.login(username='admin', password='testpass123')
        self.assertTrue(logged, "Falla login en test: revisa credenciales")
        # Para probar la lógica de rechazar reservas, creamos reservas futuras del espacio
        hoy = date.today()
        # Aseguramos que initial disponible sea True
        self.espacio.disponible = True
        self.espacio.save()
        reserva = Reserva.objects.create(
            espacio=self.espacio,
            usuario=self.usuario_user,
            fecha_uso=hoy + timedelta(days=2),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado=Reserva.Estado.PENDIENTE,
        )
        datos = {
            'nombre': self.espacio.nombre,
            'ubicacion': self.ubicacion.pk,
            'piso': self.espacio.piso,
            'capacidad': self.espacio.capacidad,
            'tipo': self.espacio.tipo,
            'descripcion': self.espacio.descripcion,
            'disponible': False,
        }
        resp = self.client.post(self.url, datos)
        self.assertEqual(resp.status_code, 302)
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, Reserva.Estado.RECHAZADA)
        self.assertEqual(reserva.aprobado_por, self.admin_user)
        self.assertEqual(reserva.motivo_admin, 'El espacio no se encuentra disponible')

class EspacioDeleteViewTest(TestCase, BaseEspacioTestCase):
    def setUp(self):
        super().setup_espacios()

        # Crear un espacio para borrar
        self.espacio = Espacio.objects.create(
            nombre='Sala a borrar',
            ubicacion=self.ubicacion,
            piso=1,
            capacidad=5,
            tipo='Otro',
            descripcion='Temporal',
            disponible=True,
        )
        self.url = reverse('espacio_delete', args=[self.espacio.pk])


    def test_get_delete_view_template(self):
        self.client.login(username='admin', password='testpass123')

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post_delete_view(self):
        self.client.login(username='admin', password='testpass123')

        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 302)
        exists = Espacio.objects.filter(pk=self.espacio.pk).exists()
        self.assertFalse(exists)

    def test_delete_cascada_o_integridad(self):
        self.client.login(username='admin', password='testpass123')

        reserva = Reserva.objects.create(
            usuario=self.usuario_user,
            espacio=self.espacio,
            fecha_uso=date.today() + timedelta(days=1),
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
            motivo='Reunión en otra sede',
            estado=Reserva.Estado.PENDIENTE
        )
        resp = self.client.post(self.url)

        self.assertEqual(resp.status_code, 302)

        self.assertFalse(Espacio.objects.filter(pk=self.espacio.pk).exists())
        self.assertFalse(Reserva.objects.filter(pk=reserva.pk).exists())
