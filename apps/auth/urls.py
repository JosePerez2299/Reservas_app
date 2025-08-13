from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path

from apps.usuarios.views import Dashboard, ProfileView

urlpatterns = [
    path('login/', LoginView.as_view(template_name='reservas/login.html', redirect_authenticated_user=True), name='login'), 
    path('', LoginView.as_view(template_name='reservas/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', ProfileView.as_view(), name='profile'),
    path('inicio/', Dashboard.as_view(), name='dashboard'),
]
