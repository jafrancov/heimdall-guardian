from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView


def inicio(request):
    return render(request, "inicio.html")


def reporte(request):
    return render(request, "reporte.html")


class Protegida(LoginRequiredMixin):
    pass


class Lista(Protegida, ListView):
    model = Expediente


class Crear(CreateView):
    model = Expediente


class Detalle(DetailView):
    model = Expediente


@require_POST
def borrar(request, pk):
    Expediente.objects.get(pk=pk).delete()


@permission_required("padron.change_expediente")
def editar(request, pk):
    return render(request, "editar.html")


@login_required
def exportar(request):
    return render(request, "exportar.html")
