from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import date, time, timedelta
from django.db.models import Q
from django.contrib.auth.password_validation import validate_password
from reservas.models import Ubicacion, Usuario, Espacio, Reserva, validate_username
from django.contrib.auth import get_user_model

class UbicacionModelTest(TestCase):
    """Tests para el modelo Ubicacion"""
    
    def test_ubicacion_creation(self):
        """Test creación básica de ubicación"""
        ubicacion = Ubicacion.objects.create(nombre="Sede Central")
        self.assertEqual(ubicacion.nombre, "Sede Central")
        self.assertEqual(str(ubicacion), "Sede Central")
    
    def test_ubicacion_unique_constraint(self):
        """Test que el nombre de ubicación sea único"""
        Ubicacion.objects.create(nombre="Sede Central")
        
        with self.assertRaises(IntegrityError):
            Ubicacion.objects.create(nombre="Sede Central")
    
    def test_ubicacion_max_length(self):
        """Test longitud máxima del nombre"""
        # Caso límite: exactamente 20 caracteres
        nombre_limite = "a" * 20
        ubicacion = Ubicacion(nombre=nombre_limite)
        ubicacion.full_clean()  # No debería fallar
        
        # Caso que excede: 21 caracteres
        nombre_excede = "a" * 21
        with self.assertRaises(ValidationError):
            ubicacion = Ubicacion(nombre=nombre_excede)
            ubicacion.full_clean()


class ValidateUsernameTest(TestCase):
    """Tests para el validador personalizado de username"""
    
    def test_valid_usernames(self):
        """Test usernames válidos"""
        valid_usernames = [
            "abc",           # Mínimo 3 caracteres
            "usuario123",    # Con números
            "user_name",     # Con guión bajo
            "A" * 20,        # Máximo 20 caracteres
            "testUser",      # CamelCase
        ]
        
        for username in valid_usernames:
            with self.subTest(username=username):
                try:
                    validate_username(username)
                except ValidationError:
                    self.fail(f"Username '{username}' debería ser válido")
    
    def test_username_too_short(self):
        """Test username demasiado corto"""
        short_usernames = ["", "a", "ab"]
        
        for username in short_usernames:
            with self.subTest(username=username):
                with self.assertRaises(ValidationError) as context:
                    validate_username(username)
                self.assertIn("al menos 3 caracteres", str(context.exception))
    
    def test_username_too_long(self):
        """Test username demasiado largo"""
        long_username = "a" * 21  # 21 caracteres
        
        with self.assertRaises(ValidationError) as context:
            validate_username(long_username)
        self.assertIn("no puede exceder 20 caracteres", str(context.exception))
    
    def test_username_starts_with_number(self):
        """Test username que comienza con número"""
        invalid_usernames = ["123user", "9test", "0abc"]
        
        for username in invalid_usernames:
            with self.subTest(username=username):
                with self.assertRaises(ValidationError) as context:
                    validate_username(username)
                self.assertIn("debe comenzar con una letra", str(context.exception))
    
    def test_username_starts_with_special_char(self):
        """Test username que comienza con carácter especial"""
        invalid_usernames = ["_user", "-test", "@user", "#test"]
        
        for username in invalid_usernames:
            with self.subTest(username=username):
                with self.assertRaises(ValidationError) as context:
                    validate_username(username)
                self.assertIn("debe comenzar con una letra", str(context.exception))
    
    def test_username_invalid_characters(self):
        """Test username con caracteres no permitidos"""
        invalid_usernames = [
            "user-name",     # Guión
            "user@name",     # Arroba
            "user name",     # Espacio
            "user.name",     # Punto
            "user#name",     # Hash
        ]
        
        for username in invalid_usernames:
            with self.subTest(username=username):
                with self.assertRaises(ValidationError) as context:
                    validate_username(username)
                self.assertIn("solo puede contener letras, números y guiones bajos", str(context.exception))


class UsuarioModelTest(TestCase):
    """Tests para el modelo Usuario"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.ubicacion = Ubicacion.objects.create(nombre="Sede Central")
        
        # Crear grupos si no existen
        self.grupo_admin = Group.objects.get_or_create(name=Usuario.GRUPOS.ADMINISTRADOR)[0]
        self.grupo_mod = Group.objects.get_or_create(name=Usuario.GRUPOS.MODERADOR)[0]
        self.grupo_user = Group.objects.get_or_create(name=Usuario.GRUPOS.USUARIO)[0]
    
    def test_usuario_creation(self):
        """Test creación básica de usuario"""
        usuario = Usuario.objects.create_user(
            username="testuser",
            email="test@example.com",
            piso=1,
            ubicacion=self.ubicacion
        )
        
        self.assertEqual(usuario.username, "testuser")
        self.assertEqual(usuario.email, "test@example.com")
        self.assertEqual(usuario.piso, 1)
        self.assertEqual(usuario.ubicacion, self.ubicacion)
    
    def test_username_unique_constraint(self):
        """Test que el username sea único"""
        Usuario.objects.create_user(
            username="testuser",
            email="test1@example.com",
            piso=1,
            ubicacion=self.ubicacion
        )
        
        with self.assertRaises(IntegrityError):
            Usuario.objects.create_user(
                username="testuser",
                email="test2@example.com",
                piso=1,
                ubicacion=self.ubicacion
            )
    
    def test_email_unique_constraint(self):
        """Test que el email sea único"""
        Usuario.objects.create_user(
            username="user1",
            email="test@example.com",
            piso=1,
            ubicacion=self.ubicacion
        )
        
        with self.assertRaises(IntegrityError):
            Usuario.objects.create_user(
                username="user2",
                email="test@example.com",
                piso=1,
                ubicacion=self.ubicacion
            )
    
    def test_piso_validation(self):
        """Test validación del campo piso"""
        # Piso válido (0-40)
        usuario = Usuario(
            username="testuser",
            email="test@example.com",
            password="testpass$",
            ubicacion=self.ubicacion,
            piso=0
        )

        usuario.full_clean()  # No debería fallar
        
        usuario.piso = 40
        usuario.full_clean()  # No debería fallar
        
        # Piso inválido (mayor a 40)
        usuario.piso = 41
        with self.assertRaises(ValidationError):
            usuario.full_clean()
    
    def test_is_properties(self):
        """Test propiedades is_admin, is_moderador, is_usuario"""
        usuario = Usuario.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
        
        # Inicialmente sin grupos
        self.assertFalse(usuario.is_admin)
        self.assertFalse(usuario.is_moderador)
        self.assertFalse(usuario.is_usuario)
        
        # Agregar a grupo administrador
        usuario.groups.add(self.grupo_admin)
        self.assertTrue(usuario.is_admin)
        
        # Agregar a grupo moderador
        usuario.groups.clear()
        usuario.groups.add(self.grupo_mod)
        self.assertTrue(usuario.is_moderador)
        
        # Agregar a grupo usuario
        usuario.groups.clear()
        usuario.groups.add(self.grupo_user)
        self.assertTrue(usuario.is_usuario)


class EspacioModelTest(TestCase):
    """Tests para el modelo Espacio"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.ubicacion = Ubicacion.objects.create(nombre="Sede Central")
    
    def test_espacio_creation(self):
        """Test creación básica de espacio"""
        espacio = Espacio.objects.create(
            nombre="Aula 101",
            ubicacion=self.ubicacion,
            piso=1,
            capacidad=30,
            tipo=Espacio.Tipo.SALON
        )
        
        self.assertEqual(espacio.nombre, "Aula 101")
        self.assertEqual(espacio.ubicacion, self.ubicacion)
        self.assertEqual(espacio.piso, 1)
        self.assertEqual(espacio.capacidad, 30)
        self.assertEqual(espacio.tipo, Espacio.Tipo.SALON)
        self.assertTrue(espacio.disponible)  # Default True
    
    def test_nombre_unique_constraint(self):
        """Test que el nombre del espacio sea único"""
        Espacio.objects.create(
            nombre="Aula 101",
            ubicacion=self.ubicacion,
            piso=1,
            capacidad=30,
            tipo=Espacio.Tipo.SALON
        )
        
        with self.assertRaises(IntegrityError):
            Espacio.objects.create(
                nombre="Aula 101",
                ubicacion=self.ubicacion,
                piso=2,
                capacidad=25,
                tipo=Espacio.Tipo.LABORATORIO
            )
    
    def test_nombre_validation(self):
        """Test validación del nombre del espacio"""
        # Nombres válidos
        valid_names = ["Aula101", "Lab 2", "Auditorio A", "Sala123"]
        
        for name in valid_names:
            with self.subTest(name=name):
                espacio = Espacio(
                    nombre=name,
                    ubicacion=self.ubicacion,
                    piso=1,
                    capacidad=30,
                    tipo=Espacio.Tipo.SALON
                )
                espacio.full_clean()  # No debería fallar
        
        # Nombres inválidos (no comienzan con letra)
        invalid_names = ["123Aula", " Aula", "-Lab"]
        
        for name in invalid_names:
            with self.subTest(name=name):
                with self.assertRaises(ValidationError):
                    espacio = Espacio(
                        nombre=name,
                        ubicacion=self.ubicacion,
                        piso=1,
                        capacidad=30,
                        tipo=Espacio.Tipo.SALON
                    )
                    espacio.full_clean()
    
    def test_piso_validation(self):
        """Test validación del campo piso"""
        # Casos límite válidos
        valid_pisos = [0, 1, 40]
        
        for piso in valid_pisos:
            with self.subTest(piso=piso):
                espacio = Espacio(
                    nombre=f"Aula{piso}",
                    ubicacion=self.ubicacion,
                    piso=piso,
                    capacidad=30,
                    tipo=Espacio.Tipo.SALON
                )
                espacio.full_clean()  # No debería fallar
        
        # Piso inválido
        with self.assertRaises(ValidationError):
            espacio = Espacio(
                nombre="AulaInvalida",
                ubicacion=self.ubicacion,
                piso=41,
                capacidad=30,
                tipo=Espacio.Tipo.SALON
            )
            espacio.full_clean()
    
    def test_capacidad_validation(self):
        """Test validación de capacidad"""
        # Capacidad válida (límite)
        espacio = Espacio(
            nombre="AulaGrande",
            ubicacion=self.ubicacion,
            piso=1,
            capacidad=1000,
            tipo=Espacio.Tipo.AUDITORIO
        )
        espacio.full_clean()  # No debería fallar
        
        # Capacidad inválida (excede límite)
        with self.assertRaises(ValidationError):
            espacio = Espacio(
                nombre="AulaInvalida",
                ubicacion=self.ubicacion,
                piso=1,
                capacidad=1001,
                tipo=Espacio.Tipo.AUDITORIO
            )
            espacio.full_clean()
    
    def test_str_method(self):
        """Test método __str__"""
        espacio = Espacio.objects.create(
            nombre="Aula 101",
            ubicacion=self.ubicacion,
            piso=2,
            capacidad=30,
            tipo=Espacio.Tipo.SALON
        )
        
        expected = "Aula 101 - Sede Central - 2"
        self.assertEqual(str(espacio), expected)


class ReservaModelTest(TestCase):
    """Tests para el modelo Reserva"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.ubicacion = Ubicacion.objects.create(nombre="Sede Central")
        
        self.usuario = Usuario.objects.create_user(
            username="testuser",
            email="test@example.com",
            ubicacion=self.ubicacion,
            piso=1
        )
        
        self.moderador = Usuario.objects.create_user(
            username="moderador",
            email="mod@example.com",
            ubicacion=self.ubicacion,
            piso=1
        )

        self.admin = Usuario.objects.create_user(
            username="admin",
            email="admin@example.com",
            is_superuser=True
        )
        
        # Crear grupos y asignarlos
        grupo_mod = Group.objects.get_or_create(name=Usuario.GRUPOS.MODERADOR)[0]
        grupo_admin = Group.objects.get_or_create(name=Usuario.GRUPOS.ADMINISTRADOR)[0]
        
        self.moderador.groups.add(grupo_mod)
        self.admin.groups.add(grupo_admin)
        
        self.espacio = Espacio.objects.create(
            nombre="Aula 101",
            ubicacion=self.ubicacion,
            piso=1,
            capacidad=30,
            tipo=Espacio.Tipo.SALON
        )
        
        # Fecha futura para las pruebas
        self.fecha_futura = timezone.now().date() + timedelta(days=1)
    
    def test_reserva_creation(self):
        """Test creación básica de reserva"""
        reserva = Reserva.objects.create(
            usuario=self.usuario,
            espacio=self.espacio,
            fecha_uso=self.fecha_futura,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            motivo="Clase de prueba"
        )
        
        self.assertEqual(reserva.usuario, self.usuario)
        self.assertEqual(reserva.espacio, self.espacio)
        self.assertEqual(reserva.fecha_uso, self.fecha_futura)
        self.assertEqual(reserva.estado, Reserva.Estado.PENDIENTE)
        self.assertEqual(reserva.motivo, "Clase de prueba")
    
    def test_fecha_uso_validation(self):
        """Test validación de fecha en el futuro"""
        # Fecha válida (hoy)
        reserva = Reserva(
            usuario=self.usuario,
            espacio=self.espacio,
            fecha_uso=timezone.now().date(),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            motivo="Clase de hoy"
        )
        reserva.full_clean()  # No debería fallar
        
        # Fecha inválida (pasado)
        fecha_pasada = timezone.now().date() - timedelta(days=1)
        with self.assertRaises(ValidationError) as context:
            reserva = Reserva(
                usuario=self.usuario,
                espacio=self.espacio,
                fecha_uso=fecha_pasada,
                hora_inicio=time(9, 0),
                hora_fin=time(10, 0),
                motivo="Clase del pasado"
            )
            reserva.full_clean()
        
        self.assertIn("debe ser hoy o en el futuro", str(context.exception))
    
    def test_espacio_disponible_validation(self):
        """Test validación de reservar espacio no disponible"""
        # Hacer el espacio no disponible
        self.espacio.disponible = False
        self.espacio.save()
        
        with self.assertRaises(ValidationError) as context:
            reserva = Reserva(
                usuario=self.usuario,
                espacio=self.espacio,
                fecha_uso=self.fecha_futura,
                hora_inicio=time(9, 0),
                hora_fin=time(10, 0),
                motivo="Clase de prueba"
            )
            reserva.full_clean()
        
        self.assertIn("no está disponible", str(context.exception))
    
    def test_solapamiento_horario_validation(self):
        """Test validación de solapamiento de horarios"""
        # Crear primera reserva
        Reserva.objects.create(
            usuario=self.usuario,
            espacio=self.espacio,
            fecha_uso=self.fecha_futura,
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
            motivo="Primera reserva"
        )
        
        # Casos de solapamiento que deberían fallar
        casos_solapamiento = [
            (time(8, 0), time(10, 0)),    # Inicia antes, termina durante
            (time(10, 0), time(12, 0)),   # Inicia durante, termina después
            (time(9, 30), time(10, 30)),  # Completamente dentro
            (time(8, 0), time(12, 0)),    # Completamente envuelve
            (time(9, 0), time(11, 0)),    # Exactamente igual
        ]
        
        usuarios = []
        for index in range(len(casos_solapamiento)):
            usuario = Usuario.objects.create_user(
                username=f"testuser_{index}",
                email=f"test{index}@example.com",
                ubicacion=self.ubicacion,
                piso=1
            )
            usuarios.append(usuario)
            

        for index, (hora_inicio, hora_fin) in enumerate(casos_solapamiento):
            with self.subTest(inicio=hora_inicio, fin=hora_fin):
                with self.assertRaises(ValidationError) as context:
                    reserva = Reserva(
                        usuario=usuarios[index],
                        espacio=self.espacio,
                        fecha_uso=self.fecha_futura,
                        hora_inicio=hora_inicio,
                        hora_fin=hora_fin,
                        motivo="Reserva solapada"
                    )
                    reserva.full_clean()
                
                self.assertIn("solapada", str(context.exception))
        
        # Casos válidos que NO deberían solapar
        casos_validos = [
            (time(7, 0), time(9, 0)),     # Termina justo cuando inicia la otra
            (time(11, 0), time(12, 0)),   # Inicia justo cuando termina la otra
            (time(12, 0), time(13, 0)),   # Completamente después
        ]
        
        for index, (hora_inicio, hora_fin) in enumerate(casos_validos):
            with self.subTest(inicio=hora_inicio, fin=hora_fin):
                reserva = Reserva(
                    usuario=usuarios[index],
                    espacio=self.espacio,
                    fecha_uso=self.fecha_futura,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    motivo="Reserva válida"
                )
                reserva.full_clean()  # No debería fallar
    
    def test_unique_constraint_usuario_espacio_fecha(self):
        """Test constraint único por usuario, espacio y fecha"""
        # Crear primera reserva
        Reserva.objects.create(
            usuario=self.usuario,
            espacio=self.espacio,
            fecha_uso=self.fecha_futura,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            motivo="Primera reserva"
        )
        
        # Intentar crear segunda reserva del mismo usuario, espacio y fecha
        with self.assertRaises(IntegrityError):
            Reserva.objects.create(
                usuario=self.usuario,
                espacio=self.espacio,
                fecha_uso=self.fecha_futura,
                hora_inicio=time(11, 0),
                hora_fin=time(12, 0),
                motivo="Segunda reserva"
            )
    
    def test_check_constraint_hora_inicio_menor_fin(self):
        """Test constraint de hora_inicio < hora_fin"""
        with self.assertRaises(IntegrityError):
            Reserva.objects.create(
                usuario=self.usuario,
                espacio=self.espacio,
                fecha_uso=self.fecha_futura,
                hora_inicio=time(11, 0),
                hora_fin=time(10, 0),  # Hora fin menor que inicio
                motivo="Reserva inválida"
            )
            

    def test_check_constraint_hora_inicio_igual_fin(self):
        """Test constraint cuando hora_inicio es igual a hora_fin"""
        with self.assertRaises(IntegrityError):
            Reserva.objects.create(
                usuario=self.usuario,
                espacio=self.espacio,
                fecha_uso=self.fecha_futura,
                hora_inicio=time(11, 0),
                hora_fin=time(11, 0),  # Hora fin igual a inicio
                motivo="Reserva inválida - horas iguales"
            )
    

    def test_aprobacion_por_no_admin_ni_moderador(self):
        """Test aprobación por usuario que no es administrador ni moderador"""
        reserva = Reserva.objects.create(
            usuario=self.usuario,
            espacio=self.espacio,
            fecha_uso=self.fecha_futura,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            motivo="Clase de prueba"
        )
    
        # Usuario no puede aprobar la reserva
        reserva.estado = Reserva.Estado.APROBADA
        reserva.aprobado_por = self.usuario
        reserva.motivo_admin = "Aprobado por usuario no admin ni moderador"
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_aprobacion_por_admin(self):
        """Test aprobación por administrador"""
        reserva = Reserva.objects.create(
            usuario=self.usuario,
            espacio=self.espacio,
            fecha_uso=self.fecha_futura,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            motivo="Clase de prueba"
        )
        
        # Admin puede aprobar cualquier reserva
        reserva.estado = Reserva.Estado.APROBADA
        reserva.aprobado_por = self.admin
        reserva.motivo_admin = "Aprobado por admin"
        reserva.full_clean()  # No debería fallar
    
    def test_aprobacion_por_moderador_mismo_piso_ubicacion(self):
        """Test aprobación por moderador del mismo piso y ubicación"""
        reserva = Reserva.objects.create(
            usuario=self.usuario,
            espacio=self.espacio,
            fecha_uso=self.fecha_futura,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            motivo="Clase de prueba"
        )
        
        # Moderador puede aprobar reserva de su mismo piso y ubicación
        reserva.estado = Reserva.Estado.APROBADA
        reserva.aprobado_por = self.moderador
        reserva.motivo_admin = "Aprobado por moderador"
        reserva.full_clean()  # No debería fallar
    
    def test_aprobacion_por_moderador_diferente_ubicacion(self):
        """Test que moderador no puede aprobar reserva de diferente ubicación"""
        # Crear otra ubicación y espacio
        otra_ubicacion = Ubicacion.objects.create(nombre="Otra Sede")
        otro_espacio = Espacio.objects.create(
            nombre="Aula 201",
            ubicacion=otra_ubicacion,
            piso=1,
            capacidad=25,
            tipo=Espacio.Tipo.SALON
        )
        
        reserva = Reserva.objects.create(
            usuario=self.usuario,
            espacio=otro_espacio,
            fecha_uso=self.fecha_futura,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            motivo="Clase de prueba"
        )
        
        # Moderador NO puede aprobar reserva de diferente ubicación
        with self.assertRaises(ValidationError) as context:
            reserva.estado = Reserva.Estado.APROBADA
            reserva.aprobado_por = self.moderador
            reserva.full_clean()
        
        self.assertIn("misma ubicación y piso", str(context.exception))
    
    def test_aprobacion_por_moderador_diferente_piso(self):
        """Test que moderador no puede aprobar reserva de diferente piso"""
        # Crear espacio en diferente piso
        otro_espacio = Espacio.objects.create(
            nombre="Aula 301",
            ubicacion=self.ubicacion,
            piso=3,  # Diferente piso
            capacidad=25,
            tipo=Espacio.Tipo.SALON
        )
        
        reserva = Reserva.objects.create(
            usuario=self.usuario,
            espacio=otro_espacio,
            fecha_uso=self.fecha_futura,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            motivo="Clase de prueba"
        )
        
        # Moderador NO puede aprobar reserva de diferente piso
        with self.assertRaises(ValidationError) as context:
            reserva.estado = Reserva.Estado.APROBADA
            reserva.aprobado_por = self.moderador
            reserva.full_clean()
        
        self.assertIn("misma ubicación y piso", str(context.exception))
    
    def test_aprobacion_por_usuario_normal(self):
        """Test que usuario normal no puede aprobar reservas"""
        reserva = Reserva.objects.create(
            usuario=self.usuario,
            espacio=self.espacio,
            fecha_uso=self.fecha_futura,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            motivo="Clase de prueba"
        )
        
        # Usuario normal NO puede aprobar reservas
        with self.assertRaises(ValidationError) as context:
            reserva.estado = Reserva.Estado.APROBADA
            reserva.aprobado_por = self.usuario
            reserva.full_clean()
        
        self.assertIn("Solo un administrador o moderador", str(context.exception))
    
    def test_str_method(self):
        """Test método __str__"""
        reserva = Reserva.objects.create(
            usuario=self.usuario,
            espacio=self.espacio,
            fecha_uso=self.fecha_futura,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            motivo="Clase de prueba"
        )
        
        expected = "US:testuser | ESP:Aula 101"
        self.assertEqual(str(reserva), expected)


