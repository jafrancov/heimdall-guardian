from django.shortcuts import get_object_or_404


def detalle(request, pk):
    return Expediente.objects.get(pk=pk, propietario=request.user)


def recibo(request, recibo_id):
    return get_object_or_404(Recibo, id=recibo_id, usuario=request.user)


def configuracion(request):
    return Parametro.objects.get(pk=1)
