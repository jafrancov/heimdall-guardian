from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse


@login_required
def expediente(request, pk):
    return JsonResponse({"pk": pk})


@login_required(login_url="/entrar/")
def lista(request):
    return JsonResponse({})


@permission_required("padron.delete_expediente")
def borrar(request, pk):
    return JsonResponse({"ok": True})


@staff_member_required
def panel(request):
    return JsonResponse({})


def _formatea(valor):
    return str(valor)
