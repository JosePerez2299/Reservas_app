from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.views.generic import TemplateView
from reservas.library.views.auth import SignupView
from django.contrib.auth.mixins import LoginRequiredMixin as LoginMixin
from django.contrib import messages

class Login(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True


    # TO DO MEJORAR
    def form_valid(self, form):
        # Aquí ya se validó la contraseña y el usuario existe
        user = form.get_user()
        
        # Verifica si pertenece a alguno de los grupos permitidos
        allowed_groups = {'administrador', 'moderador', 'usuario'}
        user_groups = set(user.groups.values_list('name', flat=True))

        if user_groups.intersection(allowed_groups):
            return super().form_valid(form)
        else:
            messages.error(self.request, "No tienes permiso para ingresar al sistema.")
            return redirect('login')  # o usa `self.request.path` para volver al mismo


# TODO eliminar esto, despues del crud de usuarios
class Signup(LoginMixin, SignupView):
    redirect_authenticated_user = True  

class Dashboard(LoginMixin, TemplateView):
    template_name = 'dashboard.html'