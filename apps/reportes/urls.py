from .views import EstadisticasView

from django.urls import path

urlpatterns = [
    path('', EstadisticasView.as_view(), name='reportes'),
]
