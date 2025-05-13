from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from reservas.library.forms.auth import User, UserCreationForm
from reservas.models import Espacio
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
# TODO: CRUD
from django.db.models import Q
from django.views.generic import ListView
from django.db.models import Q
from django.views.generic import ListView

class UserListView(ListView):
    model = User
    template_name = 'espacios/list.html'
    context_object_name = 'usuarios'
    paginate_by = 10


class UsuarioCreate(CreateView):
    form_class = UserCreationForm
    template_name = 'espacios/create.html'
    success_url = reverse_lazy('')  

    def form_valid(self, form):
        response = super().form_valid(form)
        return response
