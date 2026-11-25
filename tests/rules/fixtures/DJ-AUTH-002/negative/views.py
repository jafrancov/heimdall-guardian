from django.contrib.auth import mixins
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import DeleteView, DetailView, ListView


class Expedientes(LoginRequiredMixin, ListView):
    model = None


class Borrar(PermissionRequiredMixin, DeleteView):
    permission_required = "padron.delete_expediente"


class Detalle(mixins.LoginRequiredMixin, DetailView):
    model = None


class Formulario(Base):
    pass
