
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from reservas.library.forms.auth import User
from django.contrib.messages.views import SuccessMessageMixin
