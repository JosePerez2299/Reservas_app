from django.views.generic import TemplateView
from reservas.utils.views.auth import LoginView, SignupView

class HomeView(TemplateView):
    template_name = 'home.html'
    

class Login(LoginView):
    pass


class Signup(SignupView):
    pass