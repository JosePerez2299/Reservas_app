from django.http import HttpResponse
from django.urls import path
from reservas.views import * 

urlpatterns = [
    path('', Login.as_view(), name='home'), 
    path('login/', Login.as_view(), name='login'),
    path('signup/', Signup.as_view(), name='signup'), 
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    
    # TODO Logout
    path('dashboard/', Dashboard.as_view(), name='logout'),

    # TODO operaciones del crud
    path('dashboard/<str:section>/', Crud.as_view(), name='crud'),
    ]