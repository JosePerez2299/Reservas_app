from django.urls import path
from .views import *


urlpatterns = [


    path('', ReservaListView.as_view(), name='reserva'),
    # path('create/', ReservaCreateView.as_view(), name='reserva_create'),
    path('view/<int:pk>/', ReservaDetailView.as_view(), name='reserva_view'),
    path('edit/<int:pk>/', ReservaUpdateView.as_view(), name='reserva_edit'),
    path('delete/<int:pk>/', ReservaDeleteView.as_view(), name='reserva_delete'),
    path('calendario/', CalendarioReservasView.as_view(), name='calendario'),
    path('api/mes/', ReservasMonthlyCount.as_view(), name='reservas_monthly_count'),

    path("create/", wizard, name="reserva_create"),
    path("wizard/step1/", wizard_step1, name="wizard_step1"),
    path("wizard/step2/", wizard_step2, name="wizard_step2"),
    path("wizard/step3/", wizard_step3, name="wizard_step3"),

    path('api/fecha/', ReservasByDate.as_view(), name='reservas_by_date'),
    path('gestionar/<int:pk>/', ReservaApproveView.as_view(), name='reserva_approve'),
]

