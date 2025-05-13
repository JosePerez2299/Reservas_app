from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from reservas.library.views.crud import *
from reservas.library.views.auth import SignupView
from django.contrib.auth.mixins import LoginRequiredMixin as LoginMixin

class Login(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True  

# TODO eliminar esto, despues del crud de usuarios
class Signup(LoginMixin, SignupView):
    redirect_authenticated_user = True  

class Dashboard(LoginMixin, TemplateView):
    template_name = 'dashboard.html'


class Crud(CrudView):
    pass
