from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


def expediente(request, pk):
    return JsonResponse({"pk": pk})


@require_http_methods(["POST"])
def borrar(request, pk):
    return JsonResponse({"ok": True})
