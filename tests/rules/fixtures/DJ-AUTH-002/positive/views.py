from django.views import generic
from django.views.generic import ListView


class Expedientes(ListView):
    model = None


class Detalle(generic.DetailView):
    model = None
