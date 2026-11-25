from django.http import HttpResponseRedirect
from django.shortcuts import redirect


def ir(request, destino):
    if destino:
        return redirect(destino)
    return HttpResponseRedirect(request.GET["next"])
