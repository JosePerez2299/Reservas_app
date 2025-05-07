from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from reservas.utils.views.auth import SignupView

class HomeView(TemplateView):
    template_name = 'home.html'
    

class Login(LoginView):
    template_name = 'auth/login.html'
    # TO DO
    # success_url = reverse_lazy('dashboard')

    # Esto se borra cuando se cree el redireccionamiento condicional de dashboard
    def get_success_url(self):
        user = self.request.user
        print(user.groups)
        if user.groups.filter(name='administrador').exists():
            return reverse_lazy('manager_dashboard')
        else:
            return reverse_lazy('user_dashboard')


class Signup(SignupView):
    pass


# TO DO: proteger rutas, crear una vista de Dashboard, para 
class UserDashboardView(TemplateView):
    template_name = 'user/dashboard.html'
    # Aquí puedes agregar la lógica para el dashboard del usuario
    # Por ejemplo, obtener reservas, etc.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar datos al contexto si es necesario
        return context
    
class ManagerDashboardView(TemplateView):
    template_name = 'manager/dashboard.html'

    # Aquí puedes agregar la lógica para el dashboard del manager
    # Por ejemplo, estadísticas, gestión de usuarios, etc.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar datos al contexto si es necesario
        return context