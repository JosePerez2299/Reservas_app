from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

# Create your views here.
class EstadisticasView(TemplateView):
    template_name = "estadisticas/dashboard.html"