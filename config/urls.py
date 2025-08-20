"""
URL configuration for my_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, reverse
from django.conf.urls import handler404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('espacios/', include('apps.espacios.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('reservas/', include('apps.reservas.urls')),
    path('logs/', include('apps.logs.urls')),
    path('', include('apps.auth.urls')),
    
]

def custom_404(request, exception):
    return redirect(reverse('login'))

handler404 = 'config.urls.custom_404'
