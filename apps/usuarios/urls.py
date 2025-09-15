

from django.urls import path

from apps.usuarios.views import UsuarioApiView


urlpatterns = [
    path('api/search/<str:p00>/', UsuarioApiView.as_view(), name='usuario_api'),
]
