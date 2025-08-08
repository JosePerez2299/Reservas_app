
from django.urls import path
from .views import *


urlpatterns = [
    path('', EspacioListView.as_view(), name='espacios'),
    path('create/', EspacioCreateView.as_view(), name='espacio_create'),
    path('view/<int:pk>/',
         EspacioDetailView.as_view(), name='espacio_view'),
    path('edit/<int:pk>/',
         EspacioUpdateView.as_view(), name='espacio_edit'),
    path('delete/<int:pk>/',
         EspacioDeleteView.as_view(), name='espacio_delete'),
]
