
            
class GRUPOS:
    ADMINISTRADOR = 'administrador'
    MODERADOR = 'moderador'
    USUARIO = 'usuario'

class MODELOS  :
    LOGENTRY = {'label':'Actividad', 'name':'auditlog.LogEntry', 'url':'log'}
    USUARIO = {'label':'Usuarios', 'name':'usuarios.Usuario', 'url':'usuarios'}
    ESPACIO = {'label':'Espacios', 'name':'espacios.Espacio', 'url':'espacios'}
    RESERVA = {'label':'Reservas', 'name':'reservas.Reserva', 'url':'reserva'}
    dict = {
        'LogEntry': LOGENTRY,
        'Usuario': USUARIO,
        'Espacio': ESPACIO,
        'Reserva': RESERVA,
    }
    

DASHBOARD_ACCESS = {
    GRUPOS.ADMINISTRADOR: 
        [
            {'model': MODELOS.RESERVA, 'perms':['add', 'change', 'view', 'delete']},
            {'model': MODELOS.USUARIO, 'perms':['add', 'change', 'view', 'delete']},
            {'model': MODELOS.ESPACIO, 'perms':['add', 'change', 'view', 'delete']},
            {'model': MODELOS.LOGENTRY, 'perms':['view']},

        ],
    GRUPOS.MODERADOR: 
        [
            {'model': MODELOS.RESERVA, 'perms':['add', 'change', 'view', 'delete']},
            {'model': MODELOS.USUARIO, 'perms':['add', 'change', 'view', 'delete']},
            {'model': MODELOS.LOGENTRY, 'perms':['view']},

        ],
    GRUPOS.USUARIO:   
        [
            {'model': MODELOS.RESERVA, 'perms':['add', 'change', 'view', 'delete']},
            {'model': MODELOS.LOGENTRY, 'perms':['view']},

        ],
}