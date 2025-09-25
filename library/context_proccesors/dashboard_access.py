

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
        ESPACIOS = {'type': 'link', 'label': 'Espacios', 'url': 'espacios'}
        ESTADISTICAS = {'type': 'link', 'label': 'Reportes', 'url': 'reportes'}

    links_for_group = {
            GRUPOS.ADMINISTRADOR: [
                LinksTitle.INICIO,
                LinksTitle.RESERVA,
                LinksTitle.ESPACIOS,    
                LinksTitle.ESTADISTICAS,

            ],

            GRUPOS.USUARIO: [
                LinksTitle.INICIO,
                LinksTitle.RESERVA,
                LinksTitle.ESPACIOS,
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



