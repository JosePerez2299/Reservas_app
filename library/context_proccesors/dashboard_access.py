

from config.model_perms import DASHBOARD_ACCESS, MODELOS, GRUPOS


def dashboard_access(request):
    # Obtener la ruta actual
    current_path = request.path_info
    current_path = current_path.split('/')[1]
    dashboard_access = DashboardAccess(request.user)   

    return {
        "group": dashboard_access.get_group(),
        "dashboard_access": dashboard_access.get_links(),
        "current_section": current_path,    
    }


class DashboardAccess:
    
    class LinksTitle:
        INICIO = { 'type': 'link', 'label': 'Inicio', 'url': 'dashboard', }
        RESERVA = {'type': 'menu', 'label': 'Reservas', 'url': 'reserva', 'childrens': [
                        {'type': 'link', 'label': 'Listado', 'url': 'reserva'},
                        {'type': 'link', 'label': 'Calendario', 'url': 'calendario'},
                    ]}
        USUARIOS = {'type': 'link', 'label': 'Usuarios', 'url': 'usuarios'}
        ESPACIOS = {'type': 'link', 'label': 'Espacios', 'url': 'espacios'}

    links_for_group = {
            GRUPOS.ADMINISTRADOR: [
                LinksTitle.INICIO,
                LinksTitle.RESERVA,
                LinksTitle.USUARIOS,
                LinksTitle.ESPACIOS,    
            ],
            GRUPOS.MODERADOR: [
                LinksTitle.INICIO,
                LinksTitle.RESERVA,
                LinksTitle.USUARIOS,
            ],
            GRUPOS.USUARIO: [
                LinksTitle.INICIO,
                LinksTitle.RESERVA,
            ],
        }
 
    def __init__(self, user):
        self.user = user
        self.links = self.get_links_by_group(self.get_group())        

    def get_links(self):
        """
        Obtiene los links del menu
        """
        return self.links

    def get_group(self):
        """
        Obtiene el nombre del grupo del usuario
        """
        return self.user.groups.first().name if self.user.groups.exists() else GRUPOS.USUARIO
    

    def get_links_by_group(self, group):
        """
        Obtiene los links del menu segun el grupo del usuario
        """
        links = self.links_for_group[group]
        return links



