

from django.urls import path

from apps.usuarios.views import UsuarioListView, UsuarioCreateView, UsuarioDetailView, UsuarioUpdateView, UsuarioDeleteView


urlpatterns = [
    path('', UsuarioListView.as_view(), name='usuarios'),
    path('crear/', UsuarioCreateView.as_view(), name='usuario_create'),
    path('view/<int:pk>/',
         UsuarioDetailView.as_view(), name='usuario_view'),
    path('edit/<int:pk>/',
         UsuarioUpdateView.as_view(), name='usuario_edit'),
    path('delete/<int:pk>/',
         UsuarioDeleteView.as_view(), name='usuario_delete'),
]
