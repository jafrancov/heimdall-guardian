from django.shortcuts import get_object_or_404


def detalle(request, pk):
    return Expediente.objects.get(pk=pk)


def recibo(request, recibo_id):
    return get_object_or_404(Recibo, id=recibo_id)


class Vista:
    def get(self, request, pk):
        return Expediente.objects.get(id=pk)
